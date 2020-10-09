    $(document).ready(function () {


        $("#belong_module_id").change(function () {
            if(!project)
            {
                project=$.trim($("#project").val());
            }
            var data = {
                'project': project,
                'module': $("#belong_module_id").val()
            },
                url = "/Index/getapilist/"
            $.ajax({
                type: 'post',
                url: url,
                data: JSON.stringify(data),
                contentType: "application/json",
                dataType: 'json',
                success: function (data) {
                    $("#api_value").html("");
                    $("#api_value").append("<option>请选择</option>");



                    // <option>请选择</option>

                    for (let index = 0; index < data.length; index++) {
                        var temp = "<option " + 'value="' + data[index]['api_id'] + '"' + ">" + data[index]['api_value'] + "</option>";
                        $("#api_value").append(temp);

                    }

                }
                ,
                error: function () {
                    myAlert('Sorry，服务器可能开小差啦, 请重试!');
                }
            });
            


            $("#api_list").show();
            if(api_swith){
               $("#request").hide();
            }
            

        });

        $("#import_button").click(function () {



            //判断是否选择了项目，模块,填写了名称
            project_name = project;//选中的文本
            module_name = $('#belong_module_id').val();//选中的文本
            var case_name = $.trim($("#case_name").val());
            if (!project) {
                myAlert("请选择项目")
                return false;

            }
            if (!module_name || module_name=="请选择") {
                myAlert("请选择模块")
                return false;
            }

            if (!case_name) {
                myAlert("请输入用例/api名称")
                return false;
            }



            $("input.file-caption-name:nth-child(2)").attr("placeholder", "至少选择一个文件");

            $(".file-drop-zone-title").eq(1).html("拖拽文件到这里 …");


            $(".file-drop-zone-title").each(function (index, el) {
                $(this).html("拖拽文件到这里 …");

            });



        });




        $('#belong_case_id_div').on('click', function () {
            $("#select_env").hide();
            $('#select_case').modal({
                relatedTarget: this,
                onConfirm: function () {
                    $("#select_env").show();

                },
                onCancel: function () {
                    $("#select_env").show();

                }
            });
            return false;
        });
        $('#config_div').on('click', function () {
            $("#select_env").hide();
            $('#select_config').modal({
                relatedTarget: this,
                onConfirm: function () {
                    $("#select_env").show();

                },
                onCancel: function () {
                    $("#select_env").show();

                }
            });
        });


        function project_change(project_id, module_id, url) {

            var temp_project = $.trim($(project_id).val());
            var data = { "test": { "name": { "project": temp_project }, "type": "module" } };
            $.ajax({
                type: 'post',
                url: url,
                data: JSON.stringify(data),
                contentType: "application/json",
                success: function (data) {
                    module_info = data.split('replaceFlag');
                    var a = $(module_id);
                    a.empty();
                    for (var i = 0; i < module_info.length; i++) {
                        if (module_info[i] !== "") {
                            var value = module_info[i].split('^=');
                            a.prepend("<option value='" + value[0] + "' >" + value[1] + "</option>")
                        }
                    }
                    a.prepend("<option value='请选择' selected>请选择</option>");
                }
                ,
                error: function () {
                    myAlert('Sorry，服务器可能开小差啦, 请重试!');
                }
            });



        }

        function module_change(project_id, module_id, case_id, url,type) {
            var temp_project = $.trim($(project_id).val());
            var temp_module = $.trim($(module_id).val());
            var data = { "test": { "name": { "project": temp_project, "module": temp_module }, "type": type } };
            $.ajax({
                type: 'post',
                url: url,
                data: JSON.stringify(data),
                contentType: "application/json",
                success: function (data) {
                    case_info = data.split('replaceFlag');
                    var a = $(case_id);
                    var b="";
                    if(type=="case")
                    {
                        b = $("#belong_case_id");

                    }else{
                         
                         b = $("#config");
                    }
                    a.empty();
                    b.empty();
                    for (var i = 0; i < case_info.length; i++) {
                        if (case_info[i] !== "") {
                            var value = case_info[i].split('^=');
                            a.prepend("<option value='" + value[0] + "' >" + value[1] + "</option>")
                            b.prepend("<option value='" + value[0] + "' >" + value[1] + "</option>")
                        }
                    }
                    a.prepend("<option value='请选择' selected>请选择</option>");
                    b.prepend("<option value='请选择' selected>请选择</option>");


                }
                ,
                error: function () {
                    myAlert('Sorry，服务器可能开小差啦, 请重试!');
                }
            });



        }

        $("#select_case_project").change(function () {

            project_change("#select_case_project", "#select_case_moudle", "/Index/add_case/");


        });
        $("#select_case_moudle").change(function () {

            module_change("#select_case_project", "#select_case_moudle", "#select_case_case", "/Index/add_case/","case");


        });


        $("#select_case_case").change(function () {
            var id = $("#select_case_case").val();
            var temp = $("#select_case_case").find("option:selected").text();
            $('#belong_case_id option:selected').text(temp);
            $('#belong_case_id').val(id);


        })

        $("#select_case_confirm").click(function () {


            var temp = $("#select_case_case").find("option:selected").text();
            $("#belong_case_id_iput").val(temp);



            if ($("#belong_case_id_iput").val() !== '请选择') {
                var case_id = $('#belong_case_id').val();
                var case_name = $('#belong_case_id option:selected').text();
                var href = "<li class='pre_testcase_class' style=\"height: 20px;padding-top: 3px;\" id=" + case_id + "> <div style=\"width: 20px;height: 20px;float:left;margin: 0 auto;border-radius: 10px;background-color: #0f9ae0;\"></div><div><a style=\"margin-left: 30px;\" href='/Index/edit_case/" + case_id + "/' id = " + case_id + ">" + case_name + "" +
                    "</a></div><i class=\"js-remove\" onclick=remove_self('#" + case_id + "')>✖</i></li>";
                $("#pre_case").append(href);
            }


            $("#select_env").show();


            


        });


        // auto_load('#form_message', '/Index/add_case/', '#module', 'module')

        $("#select_config_project").change(function () {

            project_change("#select_config_project", "#select_config_moudle", "/Index/add_case/");


        });
        $("#select_config_moudle").change(function () {

            module_change("#select_config_project", "#select_config_moudle", "#select_config_config", "/Index/add_case/","config");


        });


        $("#select_config").change(function () {
            var id = $("#select_config_config").val();
            var temp = $("#select_config_config").find("option:selected").text();
            $('#config option:selected').text(temp);
            $('#config').val(id);


        })

 




        // $.ajax({
        //     type: 'post',
        //     url: url,
        //     data: JSON.stringify(data),
        //     contentType: "application/json",
        //     success: function (data) {
        //         if (type === 'module') {
        //             show_module(data, target)
        //         } else {
        //             show_case(data, target)
        //         }
        //     }
        //     ,
        //     error: function () {
        //         myAlert('Sorry，服务器可能开小差啦, 请重试!');
        //     }
        // });



    });


