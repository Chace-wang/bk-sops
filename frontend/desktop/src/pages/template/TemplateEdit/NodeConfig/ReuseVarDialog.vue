/**
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
    <bk-dialog
        ext-cls="common-dialog"
        :theme="'primary'"
        :mask-close="false"
        :render-directive="'if'"
        :header-position="'left'"
        :title="title"
        :auto-close="false"
        :value="isShow"
        width="600"
        @confirm="onConfirm"
        @cancel="onCancel">
        <div class="reuse-variable-dialog">
            <p v-if="createNew" class="new-var-notice">{{$t('已存在相同Key的变量，请新建变量')}}</p>
            <bk-form
                ref="form"
                :model="formData"
                :form-type="createNew ? 'vertical' : 'horizontal'"
                :rules="rules">
                <template v-if="!createNew">
                    <bk-form-item :label="$t('复用变量')" property="reused">
                        <bk-select
                            v-model="formData.reused"
                            :disabled="!formData.isReuse"
                            :popover-options="{ appendTo: 'parent' }"
                            :clearable="false">
                            <bk-option
                                v-for="(option, index) in variables"
                                :key="index"
                                :id="option.id"
                                :name="option.name">
                            </bk-option>
                        </bk-select>
                    </bk-form-item>
                    <bk-form-item :label="$t('新建变量')" property="isReuse">
                        <bk-switcher
                            :value="!formData.isReuse"
                            size="small"
                            theme="primary"
                            @change="toggleReuse">
                        </bk-switcher>
                    </bk-form-item>
                </template>
                <template v-if="!formData.isReuse || createNew">
                    <bk-form-item :label="$t('变量名称')" property="name" :required="true">
                        <bk-input name="variableName" v-model="formData.name"></bk-input>
                    </bk-form-item>
                    <bk-form-item :label="$t('变量KEY')" property="key" :required="true">
                        <bk-input name="variableKey" v-model="formData.key"></bk-input>
                    </bk-form-item>
                </template>
            </bk-form>
        </div>
    </bk-dialog>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapActions } from 'vuex'
    import { NAME_REG, STRING_LENGTH, INVALID_NAME_CHAR } from '@/constants/index.js'

    export default {
        name: 'ReuseVarDialog',
        props: {
            isShow: Boolean,
            createNew: Boolean,
            variables: Array
        },
        data () {
            const $this = this
            const reused = this.variables.length > 0 ? this.variables[0].id : ''
            return {
                formData: {
                    reused,
                    isReuse: true,
                    name: '',
                    key: ''
                },
                rules: {
                    name: [
                        {
                            required: true,
                            message: i18n.t('必填项'),
                            trigger: 'blur'
                        },
                        {
                            max: STRING_LENGTH.VARIABLE_NAME_MAX_LENGTH,
                            message: i18n.t('变量名称长度不能超过') + STRING_LENGTH.VARIABLE_NAME_MAX_LENGTH + i18n.t('个字符'),
                            trigger: 'blur'
                        },
                        {
                            regex: NAME_REG,
                            message: i18n.t('变量名称不能包含') + INVALID_NAME_CHAR + i18n.t('非法字符'),
                            trigger: 'blur'
                        }
                    ],
                    key: [
                        {
                            required: true,
                            message: i18n.t('必填项'),
                            trigger: 'blur'
                        },
                        {
                            validator (val) {
                                const reqLenth = /^\$\{\w+\}$/.test(val) ? (STRING_LENGTH.VARIABLE_KEY_MAX_LENGTH + 3) : STRING_LENGTH.VARIABLE_KEY_MAX_LENGTH
                                return val.length <= reqLenth
                            },
                            message: i18n.t('变量KEY值长度不能超过') + STRING_LENGTH.VARIABLE_KEY_MAX_LENGTH + i18n.t('个字符'),
                            trigger: 'blur'
                        },
                        {
                            // 合法变量key正则，eg:${fsdf_f32sd},fsdf_f32sd
                            regex: /(^\${[a-zA-Z_]\w*}$)|(^[a-zA-Z_]\w*$)/,
                            message: i18n.t('变量KEY由英文字母、数字、下划线组成，且不能以数字开头'),
                            trigger: 'blur'
                        },
                        {
                            validator (val) {
                                const value = /^\$\{\w+\}$/.test(val) ? val : `\${${val}}`
                                if (value in $this.constants) {
                                    return false
                                }
                                return true
                            },
                            message: i18n.t('变量KEY值已存在'),
                            trigger: 'blur'
                        }
                    ]
                }
            }
        },
        computed: {
            ...mapState({
                constants: state => state.template.constants
            }),
            title () {
                if (this.createNew) {
                    return i18n.t('创建新变量')
                }
                return i18n.t('是否复用变量')
            }
        },
        watch: {
            variables (val) {
                this.formData.reused = val.length > 0 ? this.variables[0].id : ''
            }
        },
        methods: {
            ...mapActions('template/', [
                'checkKey'
            ]),
            toggleReuse (val) {
                this.formData.isReuse = !val
            },
            onConfirm ($event) {
                if (!this.createNew && this.formData.isReuse) {
                    this.$emit('confirm', 'reuse', this.formData.reused)
                } else {
                    this.$refs.form.validate().then(async (result) => {
                        if (result) {
                            const { name, key } = this.formData
                            const checkKeyResult = await this.checkKey({ key })
                            if (!checkKeyResult.result) {
                                this.$bkMessage({
                                    message: i18n.t('变量KEY为特殊标志符变量，请修改'),
                                    theme: 'warning'
                                })
                                return
                            }
                            this.$emit('confirm', 'new', { name, key })
                        }
                    })
                }
            },
            onCancel () {
                this.$emit('cancel')
            }
        }
    }
</script>
<style lang="scss" scoped>
    .reuse-variable-dialog {
        padding: 20px 30px 30px;
        .new-var-notice {
            margin-bottom: 10px;
            font-size: 14px;
            color: #ff9c01;
        }
        .bk-form:not(.bk-form-vertical) {
            /deep/ .bk-form-content {
                margin-right: 30px;
            }
        }
    }
</style>
