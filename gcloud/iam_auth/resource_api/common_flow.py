# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from django.core.cache import cache
from django.db.models import Q

from gcloud.iam_auth.conf import SEARCH_INSTANCE_CACHE_TIME
from iam import DjangoQuerySetConverter
from iam.contrib.django.dispatcher import InvalidPageException
from iam.resource.provider import ListResult, ResourceProvider

from gcloud.common_template.models import CommonTemplate


class CommonFlowResourceProvider(ResourceProvider):
    def pre_search_instance(self, filter, page, **options):
        if page.limit == 0 or page.limit > 1000:
            raise InvalidPageException("limit in page too large")

    def search_instance(self, filter, page, **options):
        """
        common flow search instance. 没有上层资源，不需要处理 filter 的 parent
        """
        keyword = filter.keyword
        cache_keyword = "iam_search_instance_common_flow_{}".format(keyword)

        results = cache.get(cache_keyword)
        if results is None:
            queryset = (
                CommonTemplate.objects.select_related("pipeline_template")
                .filter(pipeline_template__name__icontains=keyword, is_deleted=False)
                .only("pipeline_template__name")
            )
            results = [
                {"id": str(common_flow.id), "display_name": common_flow.name}
                for common_flow in queryset[page.slice_from : page.slice_to]
            ]
            cache.set(cache_keyword, results, SEARCH_INSTANCE_CACHE_TIME)
        return ListResult(results=results, count=len(results))

    def list_attr(self, **options):
        """
        common_flow 资源没有属性，返回空
        """
        return ListResult(results=[], count=0)

    def list_attr_value(self, filter, page, **options):
        """
        common_flow 资源没有属性，返回空
        """
        return ListResult(results=[], count=0)

    def list_instance(self, filter, page, **options):
        """
        common_flow 没有上层资源，不需要处理 filter 中的 parent 字段
        """
        queryset = []
        with_path = False

        if not (filter.parent or filter.search or filter.resource_type_chain):
            queryset = CommonTemplate.objects.filter(is_deleted=False)
        elif filter.search and filter.resource_type_chain:
            # 返回结果需要带上资源拓扑路径信息
            with_path = True
            # 过滤 common_flow 名称
            common_flow_keywords = filter.search.get("common_flow", [])

            common_flow_filter = Q(is_deleted=False)

            for keyword in common_flow_keywords:
                common_flow_filter |= Q(pipeline_template__name__icontains=keyword)  # TODO 优化

            queryset = CommonTemplate.objects.filter(common_flow_filter)

        count = queryset.count()
        results = [
            {"id": str(common_flow.id), "display_name": common_flow.name}
            for common_flow in queryset[page.slice_from : page.slice_to]
        ]

        if with_path:
            results = [
                {"id": str(common_flow.id), "display_name": common_flow.name, "path": [[]]}
                for common_flow in queryset[page.slice_from : page.slice_to]
            ]

        return ListResult(results=results, count=count)

    def fetch_instance_info(self, filter, **options):
        """
        common_flow 没有定义属性，只处理 filter 中的 ids 字段
        """
        ids = []
        if filter.ids:
            ids = [int(i) for i in filter.ids]

        queryset = CommonTemplate.objects.filter(id__in=ids)
        count = queryset.count()

        results = [{"id": str(common_flow.id), "display_name": common_flow.name} for common_flow in queryset]
        return ListResult(results=results, count=count)

    def list_instance_by_policy(self, filter, page, **options):
        """
        common_flow
        """

        expression = filter.expression
        if not expression:
            return ListResult(results=[], count=0)

        key_mapping = {
            "common_flow.id": "id",
            "common_flow.owner": "pipeline_template__creator",  # TODO 优化
        }
        converter = DjangoQuerySetConverter(key_mapping)
        filters = converter.convert(expression)
        queryset = CommonTemplate.objects.filter(filters)
        count = queryset.count()

        results = [
            {"id": str(common_flow.id), "display_name": common_flow.name}
            for common_flow in queryset[page.slice_from : page.slice_to]
        ]

        return ListResult(results=results, count=count)
