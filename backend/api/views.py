import os, hashlib
import pandas as pd
from django.http import FileResponse, Http404
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status, generics
from .models import Dataset
from .serializers import DatasetSerializer

def checksum_file(fpath):
    h = hashlib.sha256()
    with open(fpath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            h.update(chunk)
    return h.hexdigest()

class UploadCSVView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request, format=None):
        file_obj = request.FILES.get('file')
        name = request.data.get('name') or (file_obj.name if file_obj else 'dataset')
        if not file_obj:
            return Response({'error':'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        ds = Dataset.objects.create(name=name, file=file_obj)
        fpath = ds.file.path
        try:
            df = pd.read_csv(fpath)
        except Exception as e:
            ds.delete()
            return Response({'error':f'Invalid CSV: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        ds.row_count = len(df)
        ds.checksum = checksum_file(fpath)
        ds.save()
        # keep last 5 datasets
        qs = Dataset.objects.order_by('-upload_time')
        to_delete = qs[5:]
        for old in to_delete:
            try: old.file.delete(save=False)
            except: pass
            old.delete()
        return Response(DatasetSerializer(ds).data, status=status.HTTP_201_CREATED)

class DatasetListView(generics.ListAPIView):
    serializer_class = DatasetSerializer
    def get_queryset(self):
        return Dataset.objects.order_by('-upload_time')[:5]

class DatasetDetailView(generics.RetrieveDestroyAPIView):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer

class DatasetDownloadView(APIView):
    def get(self, request, pk):
        try: ds = Dataset.objects.get(pk=pk)
        except Dataset.DoesNotExist: raise Http404
        return FileResponse(open(ds.file.path,'rb'), as_attachment=True, filename=os.path.basename(ds.file.path))

class DatasetRowsView(APIView):
    def get(self, request, pk):
        try: ds = Dataset.objects.get(pk=pk)
        except Dataset.DoesNotExist: raise Http404
        df = pd.read_csv(ds.file.path)
        page = int(request.GET.get('page',1))
        page_size = int(request.GET.get('page_size',50))
        start = (page-1)*page_size
        end = start+page_size
        rows = df.iloc[start:end].fillna('').to_dict(orient='records')
        return Response({'rows': rows, 'total': len(df)})

class DatasetSummaryView(APIView):
    def get(self, request, pk):
        try: ds = Dataset.objects.get(pk=pk)
        except Dataset.DoesNotExist: raise Http404
        df = pd.read_csv(ds.file.path)
        numeric = df.select_dtypes(include='number')
        stats = {}
        for col in numeric.columns:
            series = numeric[col].dropna()
            stats[col] = {
                'count': int(series.count()),
                'mean': float(series.mean()) if len(series) else None,
                'median': float(series.median()) if len(series) else None,
                'min': float(series.min()) if len(series) else None,
                'max': float(series.max()) if len(series) else None,
                'std': float(series.std()) if len(series) else None,
            }
        return Response({'summary': stats})
