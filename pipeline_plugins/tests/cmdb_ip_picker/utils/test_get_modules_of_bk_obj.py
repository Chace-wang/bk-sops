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

from django.test import TestCase

from pipeline_plugins.cmdb_ip_picker.utils import get_modules_of_bk_obj


class GetModulesOfBkObjTestCase(TestCase):
    def setUp(self):
        self.topo_tree = {
            "default": 0,
            "bk_obj_name": "业务",
            "bk_obj_id": "biz",
            "child": [
                {
                    "default": 1,
                    "bk_obj_name": "集群",
                    "bk_obj_id": "set",
                    "child": [
                        {
                            "default": 1,
                            "bk_obj_id": "module",
                            "bk_inst_id": 3,
                            "bk_obj_name": "模块",
                            "bk_inst_name": "空闲机",
                        },
                        {
                            "default": 1,
                            "bk_obj_id": "module",
                            "bk_inst_id": 4,
                            "bk_obj_name": "模块",
                            "bk_inst_name": "故障机",
                        },
                    ],
                    "bk_inst_id": 2,
                    "bk_inst_name": "空闲机池",
                },
                {
                    "default": 0,
                    "bk_obj_name": "集群",
                    "bk_obj_id": "set",
                    "child": [
                        {
                            "default": 0,
                            "bk_obj_name": "模块",
                            "bk_obj_id": "module",
                            "bk_inst_id": 5,
                            "bk_inst_name": "test1",
                        },
                        {
                            "default": 0,
                            "bk_obj_name": "模块",
                            "bk_obj_id": "module",
                            "bk_inst_id": 6,
                            "bk_inst_name": "test2",
                        },
                        {
                            "default": 0,
                            "bk_obj_name": "模块",
                            "bk_obj_id": "module",
                            "bk_inst_id": 7,
                            "bk_inst_name": "test3",
                        },
                    ],
                    "bk_inst_id": 3,
                    "bk_inst_name": "set2",
                },
                {
                    "default": 0,
                    "bk_obj_name": "集群",
                    "bk_obj_id": "set",
                    "child": [
                        {
                            "default": 0,
                            "bk_obj_name": "模块",
                            "bk_obj_id": "module",
                            "bk_inst_id": 8,
                            "bk_inst_name": "test1",
                        },
                        {
                            "default": 0,
                            "bk_obj_name": "模块",
                            "bk_obj_id": "module",
                            "bk_inst_id": 9,
                            "bk_inst_name": "test2",
                        },
                    ],
                    "bk_inst_id": 4,
                    "bk_inst_name": "set3",
                },
            ],
            "bk_inst_id": 2,
            "bk_inst_name": "蓝鲸",
        }

    def test__normal(self):
        modules1 = get_modules_of_bk_obj(self.topo_tree)
        self.assertEqual(set([mod["bk_inst_id"] for mod in modules1]), {3, 4, 5, 6, 7, 8, 9})

        modules2 = get_modules_of_bk_obj(self.topo_tree["child"][2])
        self.assertEqual(set([mod["bk_inst_id"] for mod in modules2]), {8, 9})

        modules3 = get_modules_of_bk_obj(self.topo_tree["child"][2]["child"][1])
        self.assertEqual(set([mod["bk_inst_id"] for mod in modules3]), {9})
