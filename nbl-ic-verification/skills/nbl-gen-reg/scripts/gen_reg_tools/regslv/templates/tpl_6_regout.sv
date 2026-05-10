{% set max_name_len = tpl_dict["common"]["max_name_len"]-20        %}
//========================================================
// register output process
//========================================================
{% for item_dict in tpl_dict["reg_assign_ls"] %}
assign {{ item_dict["lhs"] | lalign(max_name_len) }} = {{ "{" }}
    {% for sub_dict in item_dict["sublist"] %}
    {{ sub_dict["sub_sig"] | lalign(max_name_len) }}{{ sub_dict["sub_postfix"] }}
    {% endfor %}
    
{% endfor %}