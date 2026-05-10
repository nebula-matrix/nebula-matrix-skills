{% set ckp          = tpl_dict["ck_domain"]                     %}
{% set mdl          = tpl_dict["common"]["module_name"]         %}
{% set max_dw_len   = tpl_dict["common"]["max_dw_len"]          %}
{% set max_name_len = tpl_dict["common"]["max_name_len"]        %}
{% set grp_num      = (tpl_dict["common"]["grp_cnt"] - 1) | string    %}
//========================================================
// var declaration
//========================================================
// reg decl {{ ckp }}
{% for item_dict in tpl_dict["reg_decl"] %}
    {% set unit = item_dict["unit"]        %}
    {% set aw   = item_dict["aw"]          %}
    {% set dw   = item_dict["dw"]          %}
    {% set sig  = item_dict["sig_name"]    %}
    {% if "inner_cif_err" in sig %}
        {% set sig = sig + ckp %}
    {% endif %}
    {% if aw != Null %}
{{ unit }} [{{  aw  | ralign(max_dw_len) }}-1:0]         {{  sig  | lalign(max_name_len) }};
    {% elif  dw  !=1 and  dw  not in [Null, None] %}
{{ unit }} [{{  dw  | ralign(max_dw_len) }}-1:0]         {{  sig  | lalign(max_name_len) }};
    {% else %}
{{ unit }} {{ " " | ralign(max_dw_len+6) }}         {{  sig  | lalign(max_name_len) }};
    {% endif  %}
{% endfor %}
// tbl decl {{ ckp }}
{% if tpl_dict["common"]["have_tbl"]==True %}
{% set tbl_num=tpl_dict["common"]["tbl_cnt"] %}
{% set addr_dw=tbl_num*tpl_dict["tbl_dict"]["tbl_max_dp_aw"] %}
{% set data_dw=tbl_num*tpl_dict["tbl_dict"]["tbl_max_dw_a32"] %}
logic [{{  32  | ralign(max_dw_len) }}-1:0]         {{  ("%s_cif_rdata"%(mdl))  | lalign(max_name_len) }};  
logic {{ " " | ralign(max_dw_len+6) }}         {{  ("%s_cif_ack"%(mdl))   | lalign(max_name_len) }};
logic {{ " " | ralign(max_dw_len+6) }}         {{  ("%s_access_hit"%(mdl))| lalign(max_name_len) }};
logic {{ " " | ralign(max_dw_len+6) }}         {{  ("%s_ucor_err"%(mdl))  | lalign(max_name_len) }};
logic {{ " " | ralign(max_dw_len+6) }}         {{  ("%s_wr_err"%(mdl))    | lalign(max_name_len) }};
logic [{{ tbl_num | ralign(max_dw_len) }}-1:0]         {{ ("o_%s_tbl_req"%(mdl)) | lalign(max_name_len) }};  
logic [{{ tbl_num | ralign(max_dw_len) }}-1:0]         {{ ("o_%s_tbl_rw"%(mdl)) | lalign(max_name_len) }};  
logic [{{ addr_dw | ralign(max_dw_len) }}-1:0]         {{ ("o_%s_tbl_addr"%(mdl)) | lalign(max_name_len) }};  
logic [{{ data_dw | ralign(max_dw_len) }}-1:0]         {{ ("o_%s_tbl_wdata"%(mdl)) | lalign(max_name_len) }}; 
logic [{{ tbl_num | ralign(max_dw_len) }}-1:0]         {{ ("i_%s_tbl_ack"%(mdl)) | lalign(max_name_len) }};  
logic [{{ data_dw | ralign(max_dw_len) }}-1:0]         {{ ("i_%s_tbl_rdata"%(mdl)) | lalign(max_name_len) }};  
logic [{{ tbl_num | ralign(max_dw_len) }}-1:0]         {{ ("i_%s_tbl_status"%(mdl)) | lalign(max_name_len) }};  
{% endif %}
{% for item_dict in tpl_dict["tbl_decl"] %}
    {% set unit = item_dict["unit"]        %}
    {% set aw   = item_dict["aw"]          %}
    {% set dw   = item_dict["dw"]          %}
    {% set sig  = item_dict["sig_name"]    %}
    {% if  aw  != Null %}
{{ unit }} [{{  aw  | ralign(max_dw_len) }}-1:0]         {{  sig  | lalign(max_name_len) }};
    {% elif  dw  !=1 and  dw  not in [Null, None] %}
{{ unit }} [{{  dw  | ralign(max_dw_len) }}-1:0]         {{  sig  | lalign(max_name_len) }};
    {% else %}
{{ unit }} {{ " " | ralign(max_dw_len+6) }}         {{  sig  | lalign(max_name_len) }};
    {% endif  %}
{% endfor %}
// wreg decl {{ ckp }}
{% for item_dict in tpl_dict["wreg_decl"] %}
    {% set unit = item_dict["unit"]        %}
    {% set aw   = item_dict["aw"]          %}
    {% set dw   = item_dict["dw"]          %}
    {% set sig  = item_dict["sig_name"]    %}
    {% if  aw  != Null %}
{{ unit }} [{{  aw  | ralign(max_dw_len) }}-1:0]         {{  sig  | lalign(max_name_len) }};
    {% elif  dw  !=1 and  dw  not in [Null, None] %}
{{ unit }} [{{  dw  | ralign(max_dw_len) }}-1:0]         {{  sig  | lalign(max_name_len) }};
    {% else %}
{{ unit }} {{ " " | ralign(max_dw_len+6) }}         {{  sig  | lalign(max_name_len) }};
    {% endif  %}
{% endfor %}
{% if tpl_dict["common"]["have_wreg"]==True %}
    {% set max_dw_a32=tpl_dict["wreg_decl_dict"]["max_dw_a32"] %}
    {% if tpl_dict["wreg_decl_dict"]["rw_cnt"]>0 %}
        {% set dw=max_dw_a32*tpl_dict["wreg_decl_dict"]["rw_cnt"] %}
    {% else %}
        {% set dw=max_dw_a32 %}
    {% endif %}
logic [{{  dw  | ralign(max_dw_len) }}-1:0]         {{ (mdl+"_rw_wreg_data")  | lalign(max_name_len) }};
    {% if tpl_dict["wreg_decl_dict"]["ro_cnt"]>0 %}
        {% set dw=max_dw_a32*tpl_dict["wreg_decl_dict"]["ro_cnt"] %}
    {% else %}
        {% set dw=max_dw_a32 %}
    {% endif %}
logic [{{  dw  | ralign(max_dw_len) }}-1:0]         {{ (mdl+"_ro_wreg_data")  | lalign(max_name_len) }};
    {% if tpl_dict["wreg_decl_dict"]["sctr_cnt"]>0 %}
        {% set cnt=tpl_dict["wreg_decl_dict"]["sctr_cnt"] %}
        {% set dw =max_dw_a32*tpl_dict["wreg_decl_dict"]["sctr_cnt"] %}
    {% else %}
        {% set cnt=1 %}
        {% set dw =max_dw_a32 %}
    {% endif %}
logic [{{  cnt | ralign(max_dw_len) }}-1:0]         {{ (mdl+"_sctr_inc_en")   | lalign(max_name_len) }};
logic [{{  dw  | ralign(max_dw_len) }}-1:0]         {{ (mdl+"_sctr_inc_num")  | lalign(max_name_len) }};
    {% if tpl_dict["wreg_decl_dict"]["rctr_cnt"]>0 %}
        {% set cnt=tpl_dict["wreg_decl_dict"]["rctr_cnt"] %}
        {% set dw =max_dw_a32*tpl_dict["wreg_decl_dict"]["rctr_cnt"] %}
    {% else %}
        {% set cnt=1 %}
        {% set dw =max_dw_a32 %}
    {% endif %}
logic [{{  cnt | ralign(max_dw_len) }}-1:0]         {{ (mdl+"_rctr_inc_en")   | lalign(max_name_len) }};
logic [{{  dw  | ralign(max_dw_len) }}-1:0]         {{ (mdl+"_rctr_inc_num")  | lalign(max_name_len) }};
{% endif %}

// common decl {{ ckp }}
{% set mdl=tpl_dict["common"]["module_name"] %}
{% set dw =tpl_dict["common"]["reg_dw"]      %}
{% set aw =tpl_dict["common"]["reg_aw"]      %}
{% set grp=tpl_dict["common"]["grp_cnt"]     %}
logic {{ " "    | ralign(max_dw_len+6) }}         {{ ( "cif_"+mdl+ckp+"_req_ff" ) | lalign(max_name_len) }};
logic [{{ 3     | ralign(max_dw_len) }}-1:0]         {{ ( "cif_"+mdl+ckp+"_req_puls_ff" ) | lalign(max_name_len) }};
logic {{ " "    | ralign(max_dw_len+6) }}         {{ ( "access_tbl"+ckp ) | lalign(max_name_len) }};
logic {{ " "    | ralign(max_dw_len+6) }}         {{ ( "access_tbl_rsv"+ckp ) | lalign(max_name_len) }};
logic {{ " "    | ralign(max_dw_len+6) }}         {{ ( "access_tbl_rsv_ack"+ckp ) | lalign(max_name_len) }};
logic {{ " "    | ralign(max_dw_len+6) }}         {{ ( "access_reg_ack"+ckp ) | lalign(max_name_len) }};
logic {{ " "    | ralign(max_dw_len+6) }}         {{ ( "access_reg_ack_pre"+ckp ) | lalign(max_name_len) }};
logic {{ " "    | ralign(max_dw_len+6) }}         {{ ( "cif_ack_pre"+ckp ) | lalign(max_name_len) }};
logic [{{ dw    | ralign(max_dw_len) }}-1:0]         {{ ( "cif_rdata_pre"+ckp ) | lalign(max_name_len) }};
logic [{{ dw    | ralign(max_dw_len) }}-1:0]         {{ ( "unify_reg_rdata"+ckp ) | lalign(max_name_len) }};
logic [{{ dw    | ralign(max_dw_len) }}-1:0]         {{ ( "unify_tbl_rdata"+ckp ) | lalign(max_name_len) }};
logic [{{ grp   | ralign(max_dw_len) }}-1:0]         {{ ( "reg_wen"+ckp ) | lalign(max_name_len) }};
logic [{{ grp   | ralign(max_dw_len) }}-1:0]         {{ ( "reg_ren"+ckp ) | lalign(max_name_len) }};
logic [{{ aw    | ralign(max_dw_len) }}-1:0]         {{ ( "reg_addr" +ckp+"[%s:0]"%grp_num ) | lalign(max_name_len) }};
logic [{{ dw    | ralign(max_dw_len) }}-1:0]         {{ ( "reg_wdata"+ckp+"[%s:0]"%grp_num ) | lalign(max_name_len) }};
logic [{{ dw    | ralign(max_dw_len) }}-1:0]         {{ ( "reg_rdata"+ckp+"[%s:0]"%grp_num ) | lalign(max_name_len) }};
logic [{{ dw    | ralign(max_dw_len) }}-1:0]         {{ ( "norm_reg_rdata"+ckp ) | lalign(max_name_len) }};
logic [{{ dw    | ralign(max_dw_len) }}-1:0]         {{ ( "wide_reg_rdata_pre"+ckp ) | lalign(max_name_len) }};
logic {{ " "    | ralign(max_dw_len+6) }}         {{ ( "wide_reg_ack_pre"+ckp ) | lalign(max_name_len) }};
logic [{{ dw    | ralign(max_dw_len) }}-1:0]         {{ ( "wide_reg_rdata"+ckp ) | lalign(max_name_len) }};
logic {{ " "    | ralign(max_dw_len+6) }}         {{ ( "wide_reg_ack"+ckp ) | lalign(max_name_len) }};
logic [{{ dw    | ralign(max_dw_len) }}-1:0]         {{ ( "tbl_rdata"+ckp ) | lalign(max_name_len) }};
logic {{ " "    | ralign(max_dw_len+6) }}         {{ ( "tbl_ack"+ckp ) | lalign(max_name_len) }};
logic {{ " "    | ralign(max_dw_len+6) }}         {{ ( "cif_ucor_err"+ckp ) | lalign(max_name_len) }};
logic {{ " "    | ralign(max_dw_len+6) }}         {{ ( "cif_wr_err"+ckp ) | lalign(max_name_len) }};
logic {{ " "    | ralign(max_dw_len+6) }}         {{ ( "cif_tbl_wr_err"+ckp ) | lalign(max_name_len) }};
logic {{ " "    | ralign(max_dw_len+6) }}         {{ ( "cif_wide_reg_wr_err"+ckp ) | lalign(max_name_len) }};
logic {{ " "    | ralign(max_dw_len+6) }}         {{ ( "cif_err_info_ucor_err"+ckp ) | lalign(max_name_len) }};
logic {{ " "    | ralign(max_dw_len+6) }}         {{ ( "cif_err_info_wr_err"+ckp ) | lalign(max_name_len) }};
logic [{{ 30    | ralign(max_dw_len) }}-1:0]         {{ ( "cif_err_info_addr"+ckp ) | lalign(max_name_len) }};
logic [{{ grp   | ralign(max_dw_len) }}-1:0]         {{ ( "norm_reg_hit"+ckp ) | lalign(max_name_len) }};

{% if tpl_dict["common"]["apb_intf_en"]==True %}
logic {{ " " | lalign(max_dw_len + 6) }}         {{ ("i_cif_"+mdl+"_req")    | lalign(max_name_len) }};
logic {{ " " | lalign(max_dw_len + 6) }}         {{ ("i_cif_"+mdl+"_rw")     | lalign(max_name_len) }};
logic [{{25  | ralign(max_dw_len)}}-1:0]         {{ ("i_cif_"+mdl+"_addr")   | lalign(max_name_len) }};
logic {{ " " | lalign(max_dw_len + 6) }}         {{ ("i_cif_"+mdl+"_wdata")  | lalign(max_name_len) }};
logic {{ " " | lalign(max_dw_len + 6) }}         {{ ("i_cif_"+mdl+"_ack")    | lalign(max_name_len) }};
logic [{{32  | ralign(max_dw_len)}}-1:0]         {{ ("i_cif_"+mdl+"_rdata")  | lalign(max_name_len) }};
{% endif %}