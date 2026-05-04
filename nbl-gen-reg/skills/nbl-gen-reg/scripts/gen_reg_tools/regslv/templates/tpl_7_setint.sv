{% set ckp          = tpl_dict["ck_domain"]                 %}
{% set max_name_len = tpl_dict["common"]["max_name_len"]    %}
//========================================================
// setint process
//========================================================
{% for item_dict in tpl_dict["setint_ls"] %}
assign {{ item_dict["lhs"] | lalign(max_name_len) }} = {{ (item_dict["rhs"]) | lalign(max_name_len) }};
{% endfor %}