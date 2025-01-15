import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .ai import analyze_heart_rate
from .models import dataRecivedModel
from .serializers import DataReceivedSerializer


@csrf_exempt  # Disable CSRF for simplicity, ensure security if used in production
def my_endpoint(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body.decode('utf-8'))
            # Extract data from the request
            heart_rate = data.get("heart_rate")
            spo2 = data.get("spo2")
            humidity = data.get("humidity")
            temperature_dht = data.get("temperature_dht")
            temperature_ds = data.get("temperature_ds")
            # Save the data into the model
            data_instance = dataRecivedModel.objects.create(
                heartRate=heart_rate,
                spo2=spo2,
                humidity=humidity,
                temprature=temperature_dht,
                tempratureBody=temperature_ds,
            )
            data_instance.save()
            manage_database_rows()
            # Return a success response
            return JsonResponse({"message": "Data saved successfully"}, status=201)
        except Exception as e:
            # Handle errors
            return JsonResponse({"error": str(e)}, status=400)
    else:
        # Handle unsupported methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)
def fetch_latest_data(request):
    if request.method == 'GET':
        latest_data = dataRecivedModel.objects.last()
        if latest_data:
            data = {
                'id': latest_data.id,
                'heartRate': latest_data.heartRate,
                'spo2': latest_data.spo2,
                'humidity': latest_data.humidity,
                'temperature': latest_data.temprature,
                'temperatureBody': latest_data.tempratureBody,
            }
        else:
            data = {}
        return JsonResponse(data)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
def display_data(request):
    # Query all data from the model
    data = dataRecivedModel.objects.last()
    # Pass the data to the template
    return render(request, 'index.html', {'data': data})
def manage_database_rows():
    # Get the total number of rows in the database
    total_rows = dataRecivedModel.objects.count()
    # Check if the total rows exceed the limit
    if total_rows > 600:
        # Fetch the IDs of the oldest 500 rows (order by primary key or timestamp)
        rows_to_delete = dataRecivedModel.objects.values_list('id', flat=True).order_by('id')[:500]
        # Use `filter` to delete the rows with matching IDs
        dataRecivedModel.objects.filter(id__in=rows_to_delete).delete()
        print(f"Deleted 500 rows to maintain the row limit. Total rows now: {dataRecivedModel.objects.count()}")

class LatestSensorDataView(APIView):
    def get(self, request):
        try:
            # Fetch the latest data
            latest_data = dataRecivedModel.objects.last()
            if latest_data:
                serializer = DataReceivedSerializer(latest_data)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"message": "No data available"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
def chart_view(request):
    return render(request, 'chart.html', context={})
def analyze_heart_rate_view(request):
    if request.method == "GET":
        try:
            # Fetch the last 500 records from the model
            data_records = list(dataRecivedModel.objects.order_by('-id')[:50])
            # Prepare the data for AI analysis
            heart_rate_data = [record.heartRate for record in data_records]
            data_to_send = {
                "heartRate": heart_rate_data,
            }
            # Pass data to the AI function
            response_json = analyze_heart_rate(data_to_send)  # Send only necessary data≠
            # Return the AI's response to the frontend
            return JsonResponse(json.loads(response_json))  # Send parsed JSON response
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


