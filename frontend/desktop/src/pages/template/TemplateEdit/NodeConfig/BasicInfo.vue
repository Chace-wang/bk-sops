* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="basic-info">
        <!-- 普通插件 -->
        <bk-form
            v-if="!isSubflow"
            ref="pluginForm"
            :label-width="130"
            :model="formData"
            :rules="pluginRules">
            <bk-form-item :label="$t('标准插件')" :required="true" property="plugin" class="choose-plugin-input">
                <bk-input :value="formData.name" readonly>
                    <template slot="append">
                        <div
                            class="operate-btn"
                            @click="$emit('openSelectorPanel')">
                            {{ formData.plugin ? $t('重选') : $t('选择') }}
                        </div>
                    </template>
                </bk-input>
                <p v-if="formData.desc" class="plugin-info-desc" v-html="formData.desc"></p>
            </bk-form-item>
            <bk-form-item :label="$t('插件版本')" :required="true" property="version">
                <bk-select
                    v-model="formData.version"
                    :clearable="false"
                    @selected="$emit('versionChange', $event)">
                    <bk-option
                        v-for="item in versionList"
                        :key="item.version"
                        :id="item.version"
                        :name="item.version">
                    </bk-option>
                </bk-select>
            </bk-form-item>
            <bk-form-item :label="$t('节点名称')" :required="true" property="nodeName">
                <bk-input v-model="formData.nodeName" @change="updateData"></bk-input>
            </bk-form-item>
            <bk-form-item :label="$t('步骤名称')" property="stageName">
                <bk-input v-model="formData.stageName" @change="updateData"></bk-input>
            </bk-form-item>
            <bk-form-item :label="$t('节点标签')" property="label">
                <bk-search-select
                    primary-key="code"
                    :clearable="true"
                    :popover-zindex="2300"
                    :data="labelList"
                    :show-condition="false"
                    :show-popover-tag-change="false"
                    :values="filterLabelTree(formData.nodeLabel)"
                    @change="onLabelChange"
                    @clear="onLabelClear">
                </bk-search-select>
            </bk-form-item>
            <bk-form-item :label="$t('失败处理')" class="error-handle">
                <bk-checkbox
                    :value="formData.ignorable"
                    @change="onErrorHandlerChange($event, 'ignorable')">
                    <i class="error-handle-icon common-icon-dark-circle-i"></i>
                    {{ $t('自动忽略') }}
                </bk-checkbox>
                <bk-checkbox
                    :value="formData.skippable"
                    :disabled="formData.ignorable"
                    @change="onErrorHandlerChange($event, 'skippable')">
                    <i class="error-handle-icon common-icon-dark-circle-s"></i>
                    {{ $t('手动跳过') }}
                </bk-checkbox>
                <bk-checkbox
                    :value="formData.retryable"
                    :disabled="formData.ignorable"
                    @change="onErrorHandlerChange($event, 'retryable')">
                    <i class="error-handle-icon common-icon-dark-circle-r"></i>
                    {{ $t('手动重试') }}
                </bk-checkbox>
                <p
                    v-if="!formData.ignorable && !formData.skippable && !formData.retryable"
                    class="error-handle-tips">
                    {{ $t('未选择失败处理方式，标准插件节点如果执行失败，会导致任务中断后不可继续') }}
                </p>
                <div id="html-error-ingored-tootip" class="tips-item" style="white-space: normal;">
                    <p>{{ $t('自动忽略：标准插件节点如果执行失败，会自动忽略错误并把节点状态设置为成功。') }}</p>
                    <p>{{ $t('手动跳过：标准插件节点如果执行失败，可以人工干预，直接跳过节点的执行。') }}</p>
                    <p>{{ $t('手动重试：标准插件节点如果执行失败，可以人工干预，填写参数后重试节点。') }}</p>
                </div>
                <i v-bk-tooltips="errorHandleTipsConfig" ref="tooltipsHtml" class="bk-icon icon-question-circle form-item-tips"></i>
            </bk-form-item>
            <bk-form-item :label="$t('是否可选')">
                <bk-switcher
                    theme="primary"
                    size="small"
                    :value="formData.selectable"
                    @change="onSelectableChange">
                </bk-switcher>
            </bk-form-item>
        </bk-form>
        <!-- 子流程 -->
        <bk-form
            v-else
            ref="subflowForm"
            :label-width="130"
            :model="formData"
            :rules="subflowRules">
            <bk-form-item :label="$t('流程模板')" :required="true" property="tpl">
                <bk-input :value="formData.name" readonly>
                    <template slot="append">
                        <div
                            v-if="basicInfo.tpl"
                            class="view-subflow"
                            @click="$emit('viewSubflow', basicInfo.tpl)">
                            <i class="bk-icon common-icon-box-top-right-corner"></i>
                        </div>
                        <div class="operate-btn" @click="$emit('openSelectorPanel')">
                            {{ formData.tpl ? $t('重选') : $t('选择') }}
                        </div>
                    </template>
                </bk-input>
                <!-- 子流程版本更新 -->
                <i
                    class="common-icon-clock-inversion update-tooltip"
                    v-if="!inputLoading && subflowHasUpdate"
                    v-bk-tooltips="{
                        content: $t('版本更新'),
                        placements: ['bottom-end']
                    }"
                    @click="onUpdateSubflowVersion">
                </i>
            </bk-form-item>
            <bk-form-item :label="$t('节点名称')" :required="true" property="nodeName">
                <bk-input v-model="formData.nodeName" @change="updateData"></bk-input>
            </bk-form-item>
            <bk-form-item :label="$t('步骤名称')" property="stageName">
                <bk-input v-model="formData.stageName" @change="updateData"></bk-input>
            </bk-form-item>
            <bk-form-item :label="$t('是否可选')">
                <bk-switcher
                    theme="primary"
                    size="small"
                    :value="formData.selectable"
                    @change="onSelectableChange">
                </bk-switcher>
            </bk-form-item>
            <bk-form-item :label="$t('总是使用最新版本')">
                <bk-switcher
                    theme="primary"
                    size="small"
                    :value="formData.alwaysUseLatest"
                    @change="onAlwaysUseLatestChange">
                </bk-switcher>
                <i
                    v-bk-tooltips="{
                        width: 540,
                        placement: 'bottom-end',
                        content: $t('打开该开关后，每次创建任务会尝试使用子流程的最新版本，并且不会再提示该节点需要更新，如果子流程中增加了新的变量，在不更新子流程版本的情况下，会使用变量默认值')
                    }"
                    class="bk-icon icon-question-circle form-item-tips">
                </i>
            </bk-form-item>
        </bk-form>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapActions, mapMutations } from 'vuex'
    import { NAME_REG, STRING_LENGTH, INVALID_NAME_CHAR } from '@/constants/index.js'

    export default {
        name: 'BasicInfo',
        props: {
            nodeConfig: Object,
            basicInfo: Object,
            versionList: Array,
            isSubflow: Boolean,
            inputLoading: Boolean
        },
        data () {
            return {
                labelData: [],
                labelLoading: false,
                subflowLoading: false,
                version: this.basicInfo.version,
                formData: { ...this.basicInfo },
                pluginRules: {
                    plugin: [
                        {
                            required: true,
                            message: i18n.t('请选择插件'),
                            trigger: 'blur'
                        }
                    ],
                    version: [
                        {
                            required: true,
                            message: i18n.t('请选择插件版本'),
                            trigger: 'blur'
                        }
                    ],
                    nodeName: [
                        {
                            required: true,
                            message: i18n.t('节点名称不能为空'),
                            trigger: 'blur'
                        },
                        {
                            regex: NAME_REG,
                            message: i18n.t('节点名称不能包含') + INVALID_NAME_CHAR + i18n.t('非法字符'),
                            trigger: 'blur'
                        },
                        {
                            max: STRING_LENGTH.TEMPLATE_NODE_NAME_MAX_LENGTH,
                            message: i18n.t('节点名称长度不能超过') + STRING_LENGTH.TEMPLATE_NODE_NAME_MAX_LENGTH + i18n.t('个字符'),
                            trigger: 'blur'
                        }
                    ],
                    stageName: [
                        {
                            max: STRING_LENGTH.STAGE_NAME_MAX_LENGTH,
                            message: i18n.t('步骤名称长度不能超过') + STRING_LENGTH.STAGE_NAME_MAX_LENGTH + i18n.t('个字符'),
                            trigger: 'blur'
                        }
                    ]
                },
                subflowRules: {
                    tpl: [
                        {
                            required: true,
                            message: i18n.t('请选择流程模板'),
                            trigger: 'blur'
                        }
                    ],
                    nodeName: [
                        {
                            required: true,
                            message: i18n.t('节点名称不能为空'),
                            trigger: 'blur'
                        },
                        {
                            regex: NAME_REG,
                            message: i18n.t('节点名称不能包含') + INVALID_NAME_CHAR + i18n.t('非法字符'),
                            trigger: 'blur'
                        },
                        {
                            max: STRING_LENGTH.TEMPLATE_NODE_NAME_MAX_LENGTH,
                            message: i18n.t('节点名称长度不能超过') + STRING_LENGTH.TEMPLATE_NODE_NAME_MAX_LENGTH + i18n.t('个字符'),
                            trigger: 'blur'
                        }
                    ],
                    stageName: [
                        {
                            max: STRING_LENGTH.STAGE_NAME_MAX_LENGTH,
                            message: i18n.t('步骤名称长度不能超过') + STRING_LENGTH.STAGE_NAME_MAX_LENGTH + i18n.t('个字符'),
                            trigger: 'blur'
                        }
                    ]
                },
                errorHandleTipsConfig: {
                    allowHtml: true,
                    width: 400,
                    content: '#html-error-ingored-tootip',
                    placement: 'bottom-end'
                }
            }
        },
        computed: {
            ...mapState({
                'subprocessInfo': state => state.template.subprocess_info
            }),
            subflowHasUpdate () {
                if (!this.formData.alwaysUseLatest) {
                    return this.version !== this.basicInfo.version || this.subprocessInfo.details.some(subflow => {
                        if (
                            subflow.expired
                            && subflow.template_id === Number(this.formData.tpl)
                            && subflow.subprocess_node_id === this.nodeConfig.id
                        ) {
                            return true
                        }
                    })
                }
                return false
            },
            labelList () {
                if (this.labelLoading || this.labelData.length === 0) {
                    return []
                }
                return this.labelData.filter(groupItem => {
                    return !this.formData.nodeLabel.find(item => groupItem.code === item.group)
                })
            }
        },
        watch: {
            basicInfo (val) {
                this.formData = { ...val }
            }
        },
        created () {
            if (!this.isSubflow) { // 子流程节点不展示节点标签表单
                this.getNodeLabelList()
            }
        },
        methods: {
            ...mapMutations('template/', [
                'setNodeBasicInfo'
            ]),
            ...mapActions('template/', [
                'getLabels'
            ]),
            ...mapActions('atomForm/', [
                'loadSubflowConfig'
            ]),
            async getSubflowDetail () {
                this.subflowLoading = true
                try {
                    const resp = await this.loadSubflowConfig({ templateId: this.basicInfo.tpl, common: this.common })
                    this.version = resp.data.version
                } catch (e) {
                    console.log(e)
                } finally {
                    this.subflowLoading = false
                }
            },
            // 加载节点标签列表
            async getNodeLabelList () {
                try {
                    this.labelLoading = true
                    const resp = await this.getLabels({ limit: 0 })
                    this.labelData = this.transLabelListToGroup(resp.objects)
                } catch (e) {
                    console.log(e)
                } finally {
                    this.labelLoading = false
                }
            },
            // 标签分组
            transLabelListToGroup (list) {
                const data = []
                const groups = []
                list.forEach(item => {
                    const index = groups.findIndex(code => code === item.group.code)
                    if (index > -1) {
                        data[index].children.push(item)
                    } else {
                        const { code, name } = item.group
                        data.push({
                            code,
                            name,
                            children: [{ ...item }]
                        })
                        groups.push(item.group.code)
                    }
                })
                return data
            },
            /**
             * 由节点保存的标签数据格式，转换成 searchSelect 组件要求的 values 格式
             */
            filterLabelTree (val) {
                // 等待节点标签列表加载完成，再做筛选
                if (this.labelLoading) {
                    return []
                }

                const data = []
                val.forEach(item => {
                    const group = this.labelData.find(g => g.code === item.group)
                    const label = group.children.find(l => l.code === item.label)
                    data.push({
                        code: group.code,
                        name: group.name,
                        values: [
                            {
                                code: label.code,
                                name: label.name
                            }
                        ]
                    })
                })
                return data
            },
            onLabelChange (list) {
                const val = []
                list.forEach(item => {
                    if (item.values && item.values.length > 0) {
                        val.push({
                            label: item.values[0].code,
                            group: item.code
                        })
                    }
                })
                this.formData.nodeLabel = val
                this.updateData()
            },
            onLabelClear () {
                this.formData.nodeLabel = []
                this.updateData()
            },
            onErrorHandlerChange (val, type) {
                this.formData[type] = val
                if (type === 'ignorable' && val) {
                    this.formData.retryable = false
                    this.formData.skippable = false
                }
                this.updateData()
            },
            onSelectableChange (val) {
                this.formData.selectable = val
                this.updateData()
            },
            async onAlwaysUseLatestChange (val) {
                this.formData.alwaysUseLatest = val
                if (!val) {
                    await this.getSubflowDetail()
                }
                this.updateData()
            },
            updateData () {
                const { version, nodeName, stageName, nodeLabel, ignorable, skippable, retryable, selectable, alwaysUseLatest } = this.formData
                let data
                if (this.isSubflow) {
                    data = { nodeName, stageName, nodeLabel, selectable, alwaysUseLatest, latestVersion: this.version }
                } else {
                    data = { version, nodeName, stageName, nodeLabel, ignorable, skippable, retryable, selectable }
                }
                this.$emit('update', data)
            },
            /**
             * 子流程版本更新
             */
            onUpdateSubflowVersion () {
                if (this.inputLoading) {
                    return
                }

                this.$emit('updateSubflowVersion')
            },
            validate () {
                const comp = this.isSubflow ? this.$refs.subflowForm : this.$refs.pluginForm
                comp.clearError()
                return comp.validate()
            }
        }
    }
</script>
<style lang="scss" scoped>
    .basic-info {
        padding-right: 30px;
    }
    .error-handle {
        /deep/ .bk-form-checkbox {
            margin-right: 30px;
            &.is-disabled .bk-checkbox-text {
                color: #c4c6cc;
            }
        }
        .error-handle-icon {
            padding-right: 4px;
            color: #a6b0c7;
        }
        .error-handle-tips {
            font-size: 12px;
            line-height: 1;
            color: #ffb400;
        }
    }
    /deep/ .bk-form {
        .bk-label {
            font-size: 12px;
        }
        .bk-checkbox-text {
            font-size: 12px;
            color: #63656e;
        }
        .bk-form-control .group-box.group-append {
            display: flex;
            margin-left: -1px;
            background: #e1ecff;
            border: none;
            z-index: 11;
        }
        .form-item-tips {
            position: absolute;
            left: -24px;
            top: 7px;
            color: #c4c6cc;
            &:hover {
                color: #f4aa1a;
            }
        }
        .view-subflow {
            display: flex;
            padding: 0 10px;
            justify-content: center;
            align-items: center;
            font-size: 12px;
            color: #63656e;
            background: #fafbfd;
            border-top: 1px solid #dcdee5;
            border-bottom: 1px solid #dcdee5;
            cursor: pointer;
            &:hover {
                color: #3a84ff;
            }
        }
        .operate-btn {
            display: inline-block;
            width: 58px;
            height: 32px;
            line-height: 32px;
            font-size: 12px;
            color: #3a84ff;
            text-align: center;
            border: 1px solid #3a84ff;
            cursor: pointer;
        }
        .choose-plugin-input {
            .bk-form-input[readonly] {
                border-color: #c4c6cc !important;
            }
        }
        .plugin-info-desc {
            margin-top: 8px;
            font-size: 12px;
            color: #ff9c01;
            line-height: 1.2;
        }
        .update-tooltip {
            position: absolute;
            right: -28px;
            top: 8px;
            cursor: pointer;
            color: #3a84ff;
        }
    }
    .bk-option-content {
        &:hover {
            .open-link-icon {
                display: inline-block;
            }
        }
        .open-link-icon {
            display: none;
            float: right;
            margin-top: 10px;
        }
    }
</style>
