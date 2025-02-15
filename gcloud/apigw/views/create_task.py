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
import copy

import jsonschema
import ujson as json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from pipeline.exceptions import PipelineException
from pipeline_web.parser.validator import validate_web_pipeline_tree

from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.core.models import EngineConfig
from gcloud.apigw.decorators import mark_request_whether_is_trust
from gcloud.apigw.decorators import project_inject
from gcloud.apigw.schemas import APIGW_CREATE_TASK_PARAMS
from gcloud.common_template.models import CommonTemplate
from gcloud.conf import settings
from gcloud.constants import PROJECT
from gcloud.utils.strings import standardize_pipeline_node_name
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.constants import NON_COMMON_TEMPLATE_TYPES
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.apigw.views.utils import logger
from gcloud.apigw.validators import CreateTaskValidator
from gcloud.utils.decorators import request_validate
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import CreateTaskInterceptor
from gcloud.contrib.operate_record.decorators import record_operation
from gcloud.contrib.operate_record.constants import RecordType, OperateType, OperateSource
from packages.bkoauth.decorators import apigw_required


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
@project_inject
@request_validate(CreateTaskValidator)
@iam_intercept(CreateTaskInterceptor())
@record_operation(RecordType.task.name, OperateType.create.name, OperateSource.api.name)
def create_task(request, template_id, project_id):
    params = json.loads(request.body)
    project = request.project
    template_source = params.get("template_source", PROJECT)

    logger.info(
        "[API] create_task info, template_id: {template_id}, project_id: {project_id}, params: {params}".format(
            template_id=template_id, project_id=project.id, params=params
        )
    )

    # 兼容老版本的接口调用
    if template_source in NON_COMMON_TEMPLATE_TYPES:
        template_source = PROJECT
        try:
            tmpl = TaskTemplate.objects.select_related("pipeline_template").get(
                id=template_id, project_id=project.id, is_deleted=False
            )
        except TaskTemplate.DoesNotExist:
            result = {
                "result": False,
                "message": "template[id={template_id}] of project[project_id={project_id},biz_id={biz_id}] "
                "does not exist".format(template_id=template_id, project_id=project.id, biz_id=project.bk_biz_id),
                "code": err_code.CONTENT_NOT_EXIST.code,
            }
            return result

    else:
        try:
            tmpl = CommonTemplate.objects.select_related("pipeline_template").get(id=template_id, is_deleted=False)
        except CommonTemplate.DoesNotExist:
            result = {
                "result": False,
                "message": "common template[id={template_id}] does not exist".format(template_id=template_id),
                "code": err_code.CONTENT_NOT_EXIST.code,
            }
            return result

    app_code = getattr(request.jwt.app, settings.APIGW_APP_CODE_KEY)
    if not app_code:
        message = "app_code cannot be empty, make sure api gateway has sent correct params"
        return {"result": False, "message": message, "code": err_code.CONTENT_NOT_EXIST.code}

    try:
        params.setdefault("flow_type", "common")
        params.setdefault("constants", {})
        params.setdefault("exclude_task_nodes_id", [])
        params.setdefault("simplify_vars", [])
        jsonschema.validate(params, APIGW_CREATE_TASK_PARAMS)
    except jsonschema.ValidationError as e:
        logger.warning("[API] create_task raise prams error: %s" % e)
        message = "task params is invalid: %s" % e
        return {"result": False, "message": message, "code": err_code.REQUEST_PARAM_INVALID.code}

    create_with_tree = "pipeline_tree" in params

    pipeline_instance_kwargs = {
        "name": params["name"],
        "creator": request.user.username,
        "description": params.get("description", ""),
    }

    if create_with_tree:
        try:
            pipeline_tree = params["pipeline_tree"]
            for key, value in params["constants"].items():
                if key in pipeline_tree["constants"]:
                    if pipeline_tree["constants"][key].get("is_meta", False):
                        meta = copy.deepcopy(pipeline_tree["constants"][key])
                        pipeline_tree["constants"][key]["meta"] = meta
                    pipeline_tree["constants"][key]["value"] = value
            standardize_pipeline_node_name(pipeline_tree)
            validate_web_pipeline_tree(pipeline_tree)
        except Exception as e:
            message = "[API] create_task get invalid pipeline_tree: %s" % str(e)
            logger.exception(message)
            return {"result": False, "message": message, "code": err_code.UNKNOWN_ERROR.code}

        pipeline_instance_kwargs["pipeline_tree"] = pipeline_tree

        try:
            data = TaskFlowInstance.objects.create_pipeline_instance(template=tmpl, **pipeline_instance_kwargs)
        except PipelineException as e:
            message = "[API] create_task create pipeline error: %s" % str(e)
            logger.exception(message)
            return {"result": False, "message": message, "code": err_code.UNKNOWN_ERROR.code}
    else:
        try:
            data = TaskFlowInstance.objects.create_pipeline_instance_exclude_task_nodes(
                tmpl,
                pipeline_instance_kwargs,
                params["constants"],
                params["exclude_task_nodes_id"],
                params["simplify_vars"],
            )
        except Exception as e:
            return {"result": False, "message": str(e), "code": err_code.UNKNOWN_ERROR.code}

    task = TaskFlowInstance.objects.create(
        project=project,
        pipeline_instance=data,
        category=tmpl.category,
        template_id=template_id,
        template_source=template_source,
        create_method="api",
        create_info=app_code,
        flow_type=params.get("flow_type", "common"),
        current_flow="execute_task" if params.get("flow_type", "common") == "common" else "func_claim",
        engine_ver=EngineConfig.objects.get_engine_ver(
            project_id=project.id, template_id=template_id, template_source=template_source
        ),
    )
    return {
        "result": True,
        "data": {"task_id": task.id, "task_url": task.url, "pipeline_tree": task.pipeline_tree},
        "code": err_code.SUCCESS.code,
    }
