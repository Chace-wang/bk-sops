(function () {
    $.atoms.all_biz_execute_job_plan = [
        {
            type: "input",
            attrs: {
                name: gettext("全业务ID"),
                hookable: true,
                validation: [{
                    type: "required"
                }],
                default: "",
                hidden: false,
                placeholder: "",
                disabled: false,
                showPassword: false,
                value: ""
            },
            events: [],
            methods: {},
            tag_code: "all_biz_cc_id"
        },
        {
            type: "button",
            attrs: {
                name: " ",
                hookable: true,
                validation: [],
                default: "",
                hidden: false,
                title: gettext("拉取作业"),
                type: "",
                icon: "",
                size: "normal",
                disabled: false,
                loading: false,
                text: false
            },
            events: [],
            methods: {},
            tag_code: "pull_job_template_list"
        },
        {
            type: "select",
            attrs: {
                name: gettext("作业模板"),
                hookable: true,
                validation: [{
                    type: "required"
                }],
                default: "",
                hidden: false,
                value: "",
                items: [],
                multiple: false,
                multiple_limit: 0,
                clearable: true,
                allowCreate: false,
                remote: true,
                remote_url: "",
                remote_data_init: function(resp){
                    if (resp.result === false) {
                        show_msg(resp.message, 'error');
                    }
                    return resp.data;
                },
                hasGroup: false,
                disabled: false,
                placeholder: "",
                showRightBtn: false,
                rightBtnIcon: "bk-icon icon-chain",
                rightBtnCb: null,
                empty_text: gettext("无数据")
            },
            events: [
                {
                    source: "all_biz_cc_id",
                    type: "init",
                    action: function () {
                        const cc_id = this.get_parent && this.get_parent().get_child('all_biz_cc_id')._get_value();
                        if (cc_id !== '') {
                            this.remote_url = $.context.get('site_url') + 'pipeline/jobv3_get_job_template_list/' + cc_id + '/';
                            this.remoteMethod();
                        }
                    }
                },
                {
                    source: "all_biz_cc_id",
                    type: "change",
                    action: function (value) {
                        this.changeHook(false);
                        this.items = [];
                        this._set_value('');
                    }
                },
                {
                    source: "pull_job_template_list",
                    type: "click",
                    action: function (value) {
                        const cc_id = this.get_parent && this.get_parent().get_child('all_biz_cc_id')._get_value();
                        if (cc_id !== '') {
                            this.remote_url = $.context.get('site_url') + 'pipeline/jobv3_get_job_template_list/' + cc_id + '/';
                            this.remoteMethod();
                        }
                    }
                }
            ],
            methods: {},
            tag_code: "job_template_id"
        },
        {
            type: "select",
            attrs: {
                name: gettext("执行方案"),
                hookable: true,
                validation: [{
                    "type": "required"
                }],
                default: "",
                hidden: false,
                value: "",
                items: [],
                multiple: false,
                multiple_limit: 0,
                clearable: true,
                allowCreate: false,
                remote: true,
                remote_url: "",
                remote_data_init: function (resp) {
                    if (resp.result === false) {
                        show_msg(resp.message, 'error');
                    }
                    return resp.data;
                },
                hasGroup: false,
                disabled: false,
                placeholder: "",
                showRightBtn: false,
                rightBtnIcon: "bk-icon icon-chain",
                rightBtnCb: null,
                empty_text: gettext("无数据")
            },
            events: [
                {
                    source: "job_template_id",
                    type: "init",
                    action: function (value) {
                        this.changeHook(false);
                        const cc_id = this.get_parent && this.get_parent().get_child('all_biz_cc_id')._get_value();
                        if (!cc_id || !value) {
                            return;
                        } else {
                            this.remote_url = $.context.get('site_url') + 'pipeline/jobv3_get_job_plan_list/' + cc_id + '/' + value + '/';
                            this.remoteMethod();
                        }
                    }
                },
                {
                    source: "job_template_id",
                    type: "change",
                    action: function (value) {
                        this.changeHook(false);
                        this._set_value('');
                        this.items = [];
                        const cc_id = this.get_parent && this.get_parent().get_child('all_biz_cc_id')._get_value();
                        if (!cc_id || !value) {
                            return;
                        } else {
                            this.remote_url = $.context.get('site_url') + 'pipeline/jobv3_get_job_plan_list/' + cc_id + '/' + value + '/';
                            this.remoteMethod();
                        }
                    }
                }
            ],
            methods: {},
            tag_code: "job_plan_id"
        },
        {
            tag_code: "job_global_var",
            type: "datatable",
            attrs: {
                pagination: true,
                name: gettext("全局变量"),
                hookable: true,
                deleteable: false,
                empty_text: gettext("没选中作业模板或当前作业模板全局变量为空"),
                columns: [
                    {
                        tag_code: "name",
                        type: "text",
                        attrs: {
                            name: gettext("参数名称"),
                        }
                    },
                    {
                        tag_code: "type",
                        type: "category",
                        attrs: {
                            name: gettext("参数类型"),
                            hidden: true,
                        }
                    },
                    {
                        tag_code: "value",
                        type: "textarea",
                        attrs: {
                            name: gettext("参数值"),
                            editable: true
                        }
                    },
                    {
                        tag_code: "description",
                        type: "text",
                        attrs: {
                            name: gettext("描述")
                        }
                    }
                ],
            },
            events: [
                {
                    source: "all_biz_cc_id",
                    type: "init",
                    action: function () {
                        this.table_buttons = [{
                            text: gettext("刷新全局变量"),
                            callback: function () {
                                const plan_id = this.get_parent().get_child("job_plan_id").value;
                                var $this = this;
                                this.changeHook(false);
                                if (plan_id === '') {
                                    this._set_value([]);
                                    return;
                                }
                                this.set_loading(true);
                                const cc_id = this.get_parent && this.get_parent().get_child('all_biz_cc_id')._get_value();
                                $.ajax({
                                    url: $.context.get('site_url') + 'pipeline/jobv3_get_job_plan_detail/' + cc_id + '/' + plan_id + '/',
                                    type: 'GET',
                                    dataType: 'json',
                                    success: function (resp) {
                                        var global_var = $this._get_value();
                                        if (global_var) {
                                            var new_global_var = resp.data.map(function (item) {
                                                var target = global_var.find(function (old_item) {
                                                    return old_item.name === item.name;
                                                });
                                                if (target) {
                                                    item.value = target.value;
                                                }
                                                return item;
                                            })
                                            $this._set_value(new_global_var);
                                        }
                                        $this.set_loading(false);
                                        if (resp.result === false) {
                                            show_msg(resp.message, 'error');
                                        }
                                    },
                                    error: function () {
                                        $this._set_value([]);
                                        $this.set_loading(false);
                                        show_msg('request job detail error', 'error');
                                    }
                                });
                            }
                        }]
                    }
                },
                {
                    source: "job_plan_id",
                    type: "change",
                    action: function (value) {
                        var $this = this;
                        this.changeHook(false);
                        if (value === '') {
                            this._set_value([]);
                            return;
                        }
                        this.set_loading(true);
                        const cc_id = this.get_parent && this.get_parent().get_child('all_biz_cc_id')._get_value();
                        $.ajax({
                            url: $.context.get('site_url') + 'pipeline/jobv3_get_job_plan_detail/' + cc_id + '/' + value + '/',
                            type: 'GET',
                            dataType: 'json',
                            success: function (resp) {
                                if (resp.result === false) {
                                    show_msg(resp.message, 'error');
                                } else {
                                    $this._set_value(resp.data)
                                }
                                $this.set_loading(false);
                            },
                            error: function () {
                                $this._set_value([]);
                                $this.set_loading(false);
                                show_msg('request job detail error', 'error');
                            }
                        });
                    }
                }
            ]
        },
        {
            tag_code: "ip_is_exist",
            type: "radio",
            attrs: {
                name: gettext("IP 存在性校验"),
                items: [
                    {value: true, name: gettext("是")},
                    {value: false, name: gettext("否")},
                ],
                default: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        }
    ]
})();