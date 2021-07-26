import operator

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from sage_cache.services.cache_funcs import filter_related_from_cache, filter_from_cache


class CacheFilterBackend(DjangoFilterBackend):
    """Integrated with cache
    filter foreign_key/attribute from cache
    """

    @property
    def template(self):
        return 'sage_cache/form.html'

    def get_filterset(self, request, queryset, view):
        """get filterset"""
        filterset_class = self.get_filterset_class(view, queryset)
        if not filterset_class:
            return None
        kwargs = self.get_filterset_kwargs(request, None, view)  # set None as queryset because its list
        return filterset_class(**kwargs)

    def get_filterset_class(self, view, queryset=None):
        """return model class"""
        if not hasattr(view, 'model_class'):
            raise KeyError('you should set model_class in view')

        MetaBase = getattr(self.filterset_base, 'Meta', object)

        class AutoFilterSet(self.filterset_base):
            class Meta(MetaBase):
                model = view.model_class
                fields = self.get_filterset_fields(view)

        return AutoFilterSet

    def get_filterset_fields(self, view):
        """get filterset_fields from view"""
        return getattr(view, 'filterset_fields', None)

    def get_filter_depth(self, filter_kwargs: dict, level=0):
        """get depth of dictionary"""
        if not isinstance(filter_kwargs, dict) or not filter_kwargs:
            return level
        return max(self.get_filter_depth(filter_kwargs[key], level + 1) for key in filter_kwargs)

    def filter_queryset(self, request, queryset, view):
        """filter queryset from cache"""
        filter_kwargs = {}
        for param in request.query_params:
            for field in self.get_filterset_fields(view):
                if param.startswith(field):
                    sub_fields = field.split('__')
                    length = len(sub_fields)
                    if length == 1:  # filter field has no foreign key
                        filter_kwargs[sub_fields[0]] = request.query_params[param]
                    else:  # filter field has foreign key
                        for i in range(length):
                            try:
                                filter_kwargs[sub_fields[i]] = {sub_fields[i + 1]: None}
                            except IndexError:
                                filter_kwargs[sub_fields[i - 1]][sub_fields[i]] = request.query_params[param]

        filter_depth = self.get_filter_depth(filter_kwargs)  # get depth of dict
        if filter_depth == 1:  # filter has no foreign key
            return filter_from_cache(queryset, **filter_kwargs)
        return filter_related_from_cache(queryset, **filter_kwargs)  # filter with foreign key


class CacheSearchBackend(SearchFilter):
    """Integrated with cache
    search in cache via `contains` operator
    """

    def filter_queryset(self, request, queryset, view):
        search_fields = self.get_search_fields(view, request)
        search_terms = self.get_search_terms(request)

        if not search_fields or not search_terms:
            return queryset

        filter_kwargs = {}
        for field in search_fields:
            sub_fields = field.split('__')
            length = len(sub_fields)
            for i in range(length):
                try:
                    filter_kwargs[sub_fields[i]] = {sub_fields[i + 1]: None}
                except IndexError:
                    if i == 0:
                        filter_kwargs[sub_fields[i]] = search_terms[i]
                    else:
                        filter_kwargs[sub_fields[i - 1]][sub_fields[i]] = search_terms[i]

        queryset = filter_from_cache(queryset, operator_=operator.contains, **filter_kwargs)

        return queryset
