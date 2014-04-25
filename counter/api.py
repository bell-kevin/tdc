from rest_framework import serializers, viewsets, routers
from counter.models import Query


class QuerySerializer(serializers.HyperlinkedModelSerializer):
    count = serializers.CharField(source='count', read_only=True)

    class Meta:
        model = Query
        fields = ('url', 'name', 'count')

class QueryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Query.objects.all()
    serializer_class = QuerySerializer

router = routers.DefaultRouter()
router.register(r'query', QueryViewSet)
