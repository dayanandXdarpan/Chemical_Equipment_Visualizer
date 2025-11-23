from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.db.models import Count, Min, Max, StdDev, Avg
import pandas as pd
import numpy as np
import io
import re
from .models import Dataset, Equipment, DynamicData
from .serializers import DatasetSerializer, DatasetSummarySerializer, EquipmentSerializer
from .dynamic_csv_handler import (
    process_dynamic_csv, 
    calculate_dynamic_statistics,
    create_visualizations_config
)


def extract_numeric_value(value):
    """
    Extract numeric value from string that may contain units or text
    Examples: '120 L/min' -> 120, '45°C' -> 45, 'N/A' -> None, 'Ambient' -> None
    """
    if pd.isna(value):
        return None
    
    # If already numeric, return as-is
    if isinstance(value, (int, float)):
        return float(value)
    
    # Convert to string and strip whitespace
    value_str = str(value).strip()
    
    # Check for common non-numeric indicators
    if value_str.upper() in ['N/A', 'NA', 'NONE', 'NULL', '', 'AMBIENT', 'ROOM TEMP', 'ATMOSPHERIC']:
        return None
    
    # Extract first number (including decimals) from string
    match = re.search(r'-?\d+\.?\d*', value_str)
    if match:
        return float(match.group())
    
    return None


class DatasetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Dataset operations
    """
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'list':
            return DatasetSummarySerializer
        return DatasetSerializer

    def list(self, request):
        """List last 5 datasets"""
        datasets = Dataset.objects.all()[:5]
        serializer = self.get_serializer(datasets, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Get detailed dataset with all equipment"""
        try:
            dataset = Dataset.objects.get(pk=pk)
            serializer = DatasetSerializer(dataset)
            return Response(serializer.data)
        except Dataset.DoesNotExist:
            return Response({'error': 'Dataset not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def upload(self, request):
        """
        Upload CSV file and parse equipment data with comprehensive validation
        """
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        csv_file = request.FILES['file']
        
        # Validate file type
        if not csv_file.name.endswith('.csv'):
            return Response({'error': 'File must be CSV format'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate file size (max 10MB)
        if csv_file.size > 10 * 1024 * 1024:
            return Response({'error': 'File size must be less than 10MB'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Read CSV file
            file_data = csv_file.read().decode('utf-8')
            df = pd.read_csv(io.StringIO(file_data))

            # Validate CSV is not empty
            if df.empty:
                return Response({'error': 'CSV file is empty'}, status=status.HTTP_400_BAD_REQUEST)

            # Validate required columns
            required_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return Response({
                    'error': f'CSV is missing required columns: {", ".join(missing_columns)}'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Smart parsing: Extract numeric values from columns that may have units
            numeric_columns = ['Flowrate', 'Pressure', 'Temperature']
            for col in numeric_columns:
                df[col] = df[col].apply(extract_numeric_value)
            
            # Remove rows where all numeric values are None (after parsing)
            df = df.dropna(subset=numeric_columns, how='all')
            
            # Validate CSV is not empty after cleaning
            if df.empty:
                return Response({
                    'error': 'CSV file contains no valid numeric data after parsing'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validate data types and values
            validation_errors = []
            validation_warnings = []
            
            # Check for rows with missing numeric values and provide warnings
            for col in numeric_columns:
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    validation_warnings.append(f'{col} has {null_count} missing or unparseable value(s) - rows will use average')
                    # Fill NaN with column mean for calculations
                    df[col].fillna(df[col].mean(), inplace=True)

            # Convert to numeric (should already be numeric after extract_numeric_value)
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # Validate value ranges (basic sanity checks)
            if 'Flowrate' in df.columns and pd.api.types.is_numeric_dtype(df['Flowrate']):
                if (df['Flowrate'] < 0).any():
                    validation_errors.append('Flowrate cannot be negative')
                if (df['Flowrate'] > 10000).any():
                    validation_errors.append('Flowrate exceeds maximum allowed value (10000)')

            if 'Pressure' in df.columns and pd.api.types.is_numeric_dtype(df['Pressure']):
                if (df['Pressure'] < 0).any():
                    validation_errors.append('Pressure cannot be negative')
                if (df['Pressure'] > 1000).any():
                    validation_errors.append('Pressure exceeds maximum allowed value (1000)')

            if 'Temperature' in df.columns and pd.api.types.is_numeric_dtype(df['Temperature']):
                if (df['Temperature'] < -273.15).any():
                    validation_errors.append('Temperature cannot be below absolute zero (-273.15°C)')
                if (df['Temperature'] > 5000).any():
                    validation_errors.append('Temperature exceeds maximum allowed value (5000°C)')

            # Validate Equipment Name and Type are strings
            if 'Equipment Name' in df.columns:
                if (df['Equipment Name'].astype(str).str.strip() == '').any():
                    validation_errors.append('Equipment Name cannot be empty')

            if 'Type' in df.columns:
                if (df['Type'].astype(str).str.strip() == '').any():
                    validation_errors.append('Equipment Type cannot be empty')

            # If there are validation errors, return them
            if validation_errors:
                return Response({
                    'error': 'Data validation failed',
                    'validation_errors': validation_errors,
                    'validation_warnings': validation_warnings if validation_warnings else None
                }, status=status.HTTP_400_BAD_REQUEST)

            # Calculate comprehensive statistics
            total_count = len(df)
            
            stats = {
                'flowrate': {
                    'mean': float(df['Flowrate'].mean()),
                    'min': float(df['Flowrate'].min()),
                    'max': float(df['Flowrate'].max()),
                    'std': float(df['Flowrate'].std()),
                    'median': float(df['Flowrate'].median())
                },
                'pressure': {
                    'mean': float(df['Pressure'].mean()),
                    'min': float(df['Pressure'].min()),
                    'max': float(df['Pressure'].max()),
                    'std': float(df['Pressure'].std()),
                    'median': float(df['Pressure'].median())
                },
                'temperature': {
                    'mean': float(df['Temperature'].mean()),
                    'min': float(df['Temperature'].min()),
                    'max': float(df['Temperature'].max()),
                    'std': float(df['Temperature'].std()),
                    'median': float(df['Temperature'].median())
                }
            }

            # Create dataset
            dataset = Dataset.objects.create(
                name=csv_file.name,
                file=csv_file,
                uploaded_by=request.user if request.user.is_authenticated else None,
                total_count=total_count,
                avg_flowrate=stats['flowrate']['mean'],
                avg_pressure=stats['pressure']['mean'],
                avg_temperature=stats['temperature']['mean']
            )

            # Create equipment records
            for idx, row in df.iterrows():
                Equipment.objects.create(
                    dataset=dataset,
                    equipment_name=str(row['Equipment Name']).strip(),
                    equipment_type=str(row['Type']).strip(),
                    flowrate=float(row['Flowrate']),
                    pressure=float(row['Pressure']),
                    temperature=float(row['Temperature'])
                )

            # Maintain only last 5 datasets
            old_datasets = Dataset.objects.all()[5:]
            for old_dataset in old_datasets:
                old_dataset.delete()

            serializer = DatasetSerializer(dataset)
            
            # Prepare response with enhanced statistics
            response_data = {
                'message': 'File uploaded successfully',
                'dataset': serializer.data,
                'statistics': {
                    'total_records': total_count,
                    'flowrate': {
                        'average': round(stats['flowrate']['mean'], 2),
                        'min': round(stats['flowrate']['min'], 2),
                        'max': round(stats['flowrate']['max'], 2),
                        'std_dev': round(stats['flowrate']['std'], 2),
                        'median': round(stats['flowrate']['median'], 2)
                    },
                    'pressure': {
                        'average': round(stats['pressure']['mean'], 2),
                        'min': round(stats['pressure']['min'], 2),
                        'max': round(stats['pressure']['max'], 2),
                        'std_dev': round(stats['pressure']['std'], 2),
                        'median': round(stats['pressure']['median'], 2)
                    },
                    'temperature': {
                        'average': round(stats['temperature']['mean'], 2),
                        'min': round(stats['temperature']['min'], 2),
                        'max': round(stats['temperature']['max'], 2),
                        'std_dev': round(stats['temperature']['std'], 2),
                        'median': round(stats['temperature']['median'], 2)
                    }
                }
            }
            
            # Add warnings if any
            if validation_warnings:
                response_data['warnings'] = validation_warnings
            
            return Response(response_data, status=status.HTTP_201_CREATED)

        except pd.errors.EmptyDataError:
            return Response({'error': 'CSV file is empty or corrupted'}, status=status.HTTP_400_BAD_REQUEST)
        except UnicodeDecodeError:
            return Response({'error': 'File encoding error. Please ensure the file is UTF-8 encoded'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': 'Failed to process CSV file',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def upload_dynamic(self, request):
        """
        Upload CSV file with ANY structure - automatically detects columns and generates visualizations
        This endpoint works with any CSV format, not just Equipment data
        """
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        csv_file = request.FILES['file']
        
        # Validate file type
        if not csv_file.name.endswith('.csv'):
            return Response({'error': 'File must be CSV format'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate file size (max 10MB)
        if csv_file.size > 10 * 1024 * 1024:
            return Response({'error': 'File size must be less than 10MB'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Read CSV file
            file_data = csv_file.read().decode('utf-8')
            df = pd.read_csv(io.StringIO(file_data))

            # Validate CSV is not empty
            if df.empty:
                return Response({'error': 'CSV file is empty'}, status=status.HTTP_400_BAD_REQUEST)

            # Process with dynamic handler - auto-detects column types
            processed_df, metadata = process_dynamic_csv(df)
            
            if not metadata['is_valid']:
                return Response({
                    'error': 'Invalid CSV structure',
                    'details': metadata.get('error', 'Unable to detect valid data structure')
                }, status=status.HTTP_400_BAD_REQUEST)

            # Calculate statistics for ALL detected numeric columns
            column_types = metadata['column_types']
            statistics = calculate_dynamic_statistics(processed_df, column_types['numeric_columns'])
            
            # Generate visualization configurations based on detected columns
            visualizations = create_visualizations_config(column_types, processed_df.head(100))

            # Create dataset with dynamic structure
            dataset = Dataset.objects.create(
                name=csv_file.name,
                total_count=len(processed_df),
                column_structure=column_types,  # Store column structure as JSON
                statistics=statistics,  # Store all statistics as JSON
                # Legacy fields - leave null for dynamic datasets
                avg_flowrate=None,
                avg_pressure=None,
                avg_temperature=None
            )

            # Store data in DynamicData model (flexible JSON storage)
            dynamic_records = []
            for idx, row in processed_df.iterrows():
                dynamic_records.append(
                    DynamicData(
                        dataset=dataset,
                        data=row.to_dict()  # Store entire row as JSON
                    )
                )
            
            # Bulk create for better performance
            DynamicData.objects.bulk_create(dynamic_records, batch_size=1000)

            # Prepare response
            response_data = {
                'message': 'CSV file uploaded and processed successfully',
                'dataset_id': dataset.id,
                'dataset_name': dataset.name,
                'total_records': len(processed_df),
                'data_type': 'dynamic',
                'metadata': {
                    'detected_columns': {
                        'id_columns': column_types['id_columns'],
                        'category_columns': column_types['category_columns'],
                        'numeric_columns': column_types['numeric_columns']
                    },
                    'total_columns': len(df.columns),
                    'sample_data': processed_df.head(5).to_dict('records')
                },
                'statistics': statistics,
                'visualizations': visualizations,
                'warnings': metadata.get('warnings', [])
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)

        except pd.errors.EmptyDataError:
            return Response({'error': 'CSV file is empty or corrupted'}, status=status.HTTP_400_BAD_REQUEST)
        except UnicodeDecodeError:
            return Response({'error': 'File encoding error. Please ensure the file is UTF-8 encoded'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback
            return Response({
                'error': 'Failed to process CSV file',
                'details': str(e),
                'traceback': traceback.format_exc()
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def summary(self, request, pk=None):
        """
        Get summary statistics for a dataset
        """
        try:
            dataset = Dataset.objects.get(pk=pk)
            equipments = dataset.equipments.all()

            # Calculate equipment type distribution
            type_distribution = equipments.values('equipment_type').annotate(
                count=Count('equipment_type')
            )

            summary = {
                'dataset_id': dataset.id,
                'dataset_name': dataset.name,
                'uploaded_at': dataset.uploaded_at,
                'total_count': dataset.total_count,
                'averages': {
                    'flowrate': round(dataset.avg_flowrate, 2),
                    'pressure': round(dataset.avg_pressure, 2),
                    'temperature': round(dataset.avg_temperature, 2)
                },
                'type_distribution': list(type_distribution),
                'equipment_list': EquipmentSerializer(equipments, many=True).data
            }

            return Response(summary)

        except Dataset.DoesNotExist:
            return Response({'error': 'Dataset not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def export(self, request, pk=None):
        """
        Export dataset in different formats (csv, json, excel)
        """
        try:
            dataset = Dataset.objects.get(pk=pk)
            equipments = dataset.equipments.all()
            
            format_type = request.query_params.get('format', 'csv').lower()
            
            # Prepare data
            data = []
            for eq in equipments:
                data.append({
                    'Equipment Name': eq.equipment_name,
                    'Type': eq.equipment_type,
                    'Flowrate': eq.flowrate,
                    'Pressure': eq.pressure,
                    'Temperature': eq.temperature
                })
            
            df = pd.DataFrame(data)
            
            if format_type == 'json':
                return Response({
                    'dataset_name': dataset.name,
                    'exported_at': pd.Timestamp.now().isoformat(),
                    'total_records': len(data),
                    'data': data
                })
            
            elif format_type == 'csv':
                from django.http import HttpResponse
                response = HttpResponse(content_type='text/csv')
                # Ensure filename has .csv extension
                filename = dataset.name if dataset.name.endswith('.csv') else f"{dataset.name}.csv"
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                df.to_csv(response, index=False)
                return response
            
            elif format_type == 'excel':
                from django.http import HttpResponse
                import io
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Equipment Data')
                output.seek(0)
                response = HttpResponse(
                    output.read(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename="{dataset.name.replace(".csv", ".xlsx")}"'
                return response
            
            else:
                return Response({'error': 'Invalid format. Use csv, json, or excel'}, status=status.HTTP_400_BAD_REQUEST)
                
        except Dataset.DoesNotExist:
            return Response({'error': 'Dataset not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def filter_equipment(self, request, pk=None):
        """
        Filter equipment by type, value ranges
        """
        try:
            dataset = Dataset.objects.get(pk=pk)
            equipments = dataset.equipments.all()
            
            # Filter by equipment type
            eq_type = request.query_params.get('type')
            if eq_type:
                equipments = equipments.filter(equipment_type__icontains=eq_type)
            
            # Filter by flowrate range
            flowrate_min = request.query_params.get('flowrate_min')
            flowrate_max = request.query_params.get('flowrate_max')
            if flowrate_min:
                equipments = equipments.filter(flowrate__gte=float(flowrate_min))
            if flowrate_max:
                equipments = equipments.filter(flowrate__lte=float(flowrate_max))
            
            # Filter by pressure range
            pressure_min = request.query_params.get('pressure_min')
            pressure_max = request.query_params.get('pressure_max')
            if pressure_min:
                equipments = equipments.filter(pressure__gte=float(pressure_min))
            if pressure_max:
                equipments = equipments.filter(pressure__lte=float(pressure_max))
            
            # Filter by temperature range
            temp_min = request.query_params.get('temp_min')
            temp_max = request.query_params.get('temp_max')
            if temp_min:
                equipments = equipments.filter(temperature__gte=float(temp_min))
            if temp_max:
                equipments = equipments.filter(temperature__lte=float(temp_max))
            
            # Sort results
            sort_by = request.query_params.get('sort_by', 'id')
            sort_order = request.query_params.get('sort_order', 'asc')
            if sort_order == 'desc':
                sort_by = f'-{sort_by}'
            equipments = equipments.order_by(sort_by)
            
            return Response({
                'total_results': equipments.count(),
                'filtered_equipment': EquipmentSerializer(equipments, many=True).data
            })
            
        except Dataset.DoesNotExist:
            return Response({'error': 'Dataset not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def advanced_stats(self, request, pk=None):
        """
        Get advanced statistics including correlations and trends
        """
        try:
            dataset = Dataset.objects.get(pk=pk)
            equipments = dataset.equipments.all()
            
            # Get aggregated stats from database
            from django.db.models import Min, Max, Avg, StdDev
            stats = equipments.aggregate(
                flowrate_min=Min('flowrate'),
                flowrate_max=Max('flowrate'),
                flowrate_avg=Avg('flowrate'),
                flowrate_std=StdDev('flowrate'),
                pressure_min=Min('pressure'),
                pressure_max=Max('pressure'),
                pressure_avg=Avg('pressure'),
                pressure_std=StdDev('pressure'),
                temperature_min=Min('temperature'),
                temperature_max=Max('temperature'),
                temperature_avg=Avg('temperature'),
                temperature_std=StdDev('temperature'),
            )
            
            # Get equipment type statistics
            type_stats = {}
            for eq_type in equipments.values_list('equipment_type', flat=True).distinct():
                type_equipments = equipments.filter(equipment_type=eq_type)
                type_stats[eq_type] = {
                    'count': type_equipments.count(),
                    'avg_flowrate': round(type_equipments.aggregate(Avg('flowrate'))['flowrate__avg'] or 0, 2),
                    'avg_pressure': round(type_equipments.aggregate(Avg('pressure'))['pressure__avg'] or 0, 2),
                    'avg_temperature': round(type_equipments.aggregate(Avg('temperature'))['temperature__avg'] or 0, 2),
                }
            
            return Response({
                'dataset_id': dataset.id,
                'overall_statistics': {
                    'flowrate_min': round(stats['flowrate_min'] or 0, 2),
                    'flowrate_max': round(stats['flowrate_max'] or 0, 2),
                    'flowrate_avg': round(stats['flowrate_avg'] or 0, 2),
                    'flowrate_std': round(stats['flowrate_std'] or 0, 2),
                    'pressure_min': round(stats['pressure_min'] or 0, 2),
                    'pressure_max': round(stats['pressure_max'] or 0, 2),
                    'pressure_avg': round(stats['pressure_avg'] or 0, 2),
                    'pressure_std': round(stats['pressure_std'] or 0, 2),
                    'temperature_min': round(stats['temperature_min'] or 0, 2),
                    'temperature_max': round(stats['temperature_max'] or 0, 2),
                    'temperature_avg': round(stats['temperature_avg'] or 0, 2),
                    'temperature_std': round(stats['temperature_std'] or 0, 2),
                },
                'by_equipment_type': type_stats
            })
            
        except Dataset.DoesNotExist:
            return Response({'error': 'Dataset not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user - Email is now mandatory for password recovery
    """
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    if not username or not password or not email:
        return Response({'error': 'Username, email, and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password, email=email)
    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        'message': 'User registered successfully',
        'token': token.key,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Login user and return token
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if user is None:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        'message': 'Login successful',
        'token': token.key,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    Logout user by deleting token
    """
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Logout successful'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
