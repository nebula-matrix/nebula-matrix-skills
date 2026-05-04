{% set ckp          = tpl_dict["ck_domain"]                     %}
{% set mdl          = tpl_dict["common"]["module_name"] + ckp   %}
{% set max_name_len = tpl_dict["common"]["max_name_len"]        %}
{% set reg_dw       = tpl_dict["common"]["reg_dw"] | string     %}
//========================================================
// output process {{ ckp }}
//========================================================
// process tbl input and output
{% if tpl_dict["common"]["have_tbl"]==True %}
assign {{ tpl_dict["tbl_asg_dict"]["tbl_ack_lhs"] | lalign(max_name_len) }} = {{ tpl_dict["tbl_asg_dict"]["tbl_ack_rhs"] | lalign(max_name_len) }};
assign {{ tpl_dict["tbl_asg_dict"]["tbl_rdata_lhs"] | lalign(max_name_len) }} = {{ tpl_dict["tbl_asg_dict"]["tbl_rdata_rhs"] | lalign(max_name_len) }};
assign {{ tpl_dict["tbl_asg_dict"]["tbl_status_lhs"] | lalign(max_name_len) }} = {{ tpl_dict["tbl_asg_dict"]["tbl_status_rhs"] | lalign(max_name_len) }};
    {% for item_dict in tpl_dict["tbl_asg_dict"]["output_tbl_asg"] %}
assign {{ item_dict["lhs"] | lalign(max_name_len) }} = {{ item_dict["rhs"] | lalign(max_name_len) }};
    {% endfor %}
{% endif %}

// process wide reg input and output
{% for item_dict in tpl_dict["wreg_op_assign_ls"] %}
assign {{ item_dict["lhs_sig"] | lalign(max_name_len) }} = {{ item_dict["rhs_sig"] | lalign(max_name_len) }};
{% endfor %}
{% if tpl_dict["common"]["have_wreg"]==True %}
// rw wreg
    {% for item_dict in tpl_dict["wreg_asg_dict"]["rw_ls"] %}
assign {{ item_dict["lhs"] | lalign(max_name_len) }} = {{ item_dict["rhs"] | lalign(max_name_len) }};   
    {% endfor %}
// ro wreg
assign {{ tpl_dict["wreg_asg_dict"]["ro_lhs"] | lalign(max_name_len) }} = {{ tpl_dict["wreg_asg_dict"]["ro_rhs"] | lalign(max_name_len) }};   
// sctr wreg
assign {{ tpl_dict["wreg_asg_dict"]["sctr_inc_en_lhs"]  | lalign(max_name_len) }} = {{ tpl_dict["wreg_asg_dict"]["sctr_inc_en_rhs"]     | lalign(max_name_len) }};   
assign {{ tpl_dict["wreg_asg_dict"]["sctr_inc_num_lhs"] | lalign(max_name_len) }} = {{ tpl_dict["wreg_asg_dict"]["sctr_inc_num_rhs"]    | lalign(max_name_len) }};   
// rctr wreg
assign {{ tpl_dict["wreg_asg_dict"]["rctr_inc_en_lhs"]  | lalign(max_name_len) }} = {{ tpl_dict["wreg_asg_dict"]["rctr_inc_en_rhs"]     | lalign(max_name_len) }};   
assign {{ tpl_dict["wreg_asg_dict"]["rctr_inc_num_lhs"] | lalign(max_name_len) }} = {{ tpl_dict["wreg_asg_dict"]["rctr_inc_num_rhs"]    | lalign(max_name_len) }};
{% else %} 
assign {{ ("wide_reg_ack" + ckp)   | lalign(max_name_len) }} = {{ "1'b0"            | lalign(max_name_len) }};
assign {{ ("wide_reg_rdata" + ckp) | lalign(max_name_len) }} = {{ (reg_dw+"'b0")    | lalign(max_name_len) }};
{% endif %}

// process reg input and output
{% for item_dict in tpl_dict["op_assign_ls"] %}
assign {{ item_dict["lhs_sig"] | lalign(max_name_len) }} = {{ item_dict["rhs_sig"] | lalign(max_name_len) }};
{% endfor %}