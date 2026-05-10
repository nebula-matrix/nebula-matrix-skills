//========================================================
// cross clock
//========================================================
{% set max_dw_len   =tpl_dict["common"]["max_dw_len"] %}
{% set max_sp_len   =tpl_dict["common"]["max_dw_len"]+6 %}
{% set max_name_len =tpl_dict["common"]["max_name_len"] %}
{% set mdl          =tpl_dict["common"]["module_name"] %}
{% set clk          =tpl_dict["common"]["clk"] %}
{% set rst          =tpl_dict["common"]["rst"] %}
{% set ck0          ="_"+tpl_dict["common"]["clk_ls"][0] %}
{% set ck1          ="_"+tpl_dict["common"]["clk_ls"][-1] %}
{% set dw =tpl_dict["common"]["reg_dw"]  %}
{% set aw =tpl_dict["common"]["reg_aw"]  %}

{% if tpl_dict["common"]["have_int"]==True %}
{% set ck0_int      ="o_reg_"+mdl+ck0+"_interupt"      %}
{% set ck0_int_sync ="o_reg_"+mdl+ck0+"_interupt_sync" %}
{% set ck1_int      ="o_reg_"+mdl+ck1+"_interupt"      %}
{% set ck1_int_sync ="o_reg_"+mdl+ck1+"_interupt_sync" %}
logic {{ " "    | ralign(max_sp_len) }}         {{ ck0_int      | lalign(max_name_len) }};
logic {{ " "    | ralign(max_sp_len) }}         {{ ck0_int_sync | lalign(max_name_len) }};
logic {{ " "    | ralign(max_sp_len) }}         {{ ck1_int      | lalign(max_name_len) }};
logic {{ " "    | ralign(max_sp_len) }}         {{ ck1_int_sync | lalign(max_name_len) }};
{% endif %}
// clk_part {{ck0}}
logic {{ " "    | ralign(max_sp_len) }}         {{ tpl_dict["cross_ck_dict"]["ck0_req"] | lalign(max_name_len) }};
logic {{ " "    | ralign(max_sp_len) }}         {{ tpl_dict["cross_ck_dict"]["ck0_rw"] | lalign(max_name_len) }};
logic [{{ aw    | ralign(max_dw_len) }}-1:0]         {{ tpl_dict["cross_ck_dict"]["ck0_addr"] | lalign(max_name_len) }};
logic [{{ dw    | ralign(max_dw_len) }}-1:0]         {{ tpl_dict["cross_ck_dict"]["ck0_wdata"] | lalign(max_name_len) }};
logic {{ " "    | ralign(max_sp_len) }}         {{ tpl_dict["cross_ck_dict"]["ck0_ack"] | lalign(max_name_len) }};
logic [{{ dw    | ralign(max_dw_len) }}-1:0]         {{ tpl_dict["cross_ck_dict"]["ck0_rdata"] | lalign(max_name_len) }};
// clk_part {{ck1}}
logic {{ " "    | ralign(max_sp_len) }}         {{ tpl_dict["cross_ck_dict"]["ck1_req"] | lalign(max_name_len) }};
logic {{ " "    | ralign(max_sp_len) }}         {{ tpl_dict["cross_ck_dict"]["ck1_rw"] | lalign(max_name_len) }};
logic [{{ aw    | ralign(max_dw_len) }}-1:0]         {{ tpl_dict["cross_ck_dict"]["ck1_addr"] | lalign(max_name_len) }};
logic [{{ dw    | ralign(max_dw_len) }}-1:0]         {{ tpl_dict["cross_ck_dict"]["ck1_wdata"] | lalign(max_name_len) }};
logic {{ " "    | ralign(max_sp_len) }}         {{ tpl_dict["cross_ck_dict"]["ck1_ack"] | lalign(max_name_len) }};
logic [{{ dw    | ralign(max_dw_len) }}-1:0]         {{ tpl_dict["cross_ck_dict"]["ck1_rdata"] | lalign(max_name_len) }};
logic {{ " "    | ralign(max_sp_len) }}         {{ tpl_dict["cross_ck_dict"]["mid_req"] | lalign(max_name_len) }};
logic {{ " "    | ralign(max_sp_len) }}         {{ tpl_dict["cross_ck_dict"]["mid_rw"] | lalign(max_name_len) }};
logic [{{ aw    | ralign(max_dw_len) }}-1:0]         {{ tpl_dict["cross_ck_dict"]["mid_addr"] | lalign(max_name_len) }};
logic [{{ dw    | ralign(max_dw_len) }}-1:0]         {{ tpl_dict["cross_ck_dict"]["mid_wdata"] | lalign(max_name_len) }};
logic {{ " "    | ralign(max_sp_len) }}         {{ tpl_dict["cross_ck_dict"]["mid_ack"] | lalign(max_name_len) }};
logic [{{ dw    | ralign(max_dw_len) }}-1:0]         {{ tpl_dict["cross_ck_dict"]["mid_rdata"] | lalign(max_name_len) }};

sync3 #(
    .DATA_W         ( {{ 1                                      | lalign(max_name_len) }} )
) U_SYNC_INT (
    .i_clk          ( {{ (clk+ck0)                          | lalign(max_name_len) }} ),
    .i_data_in      ( {{ ("o_reg_"+mdl+ck1+"_interupt")         | lalign(max_name_len) }} ),
    .o_sync_data    ( {{ ("o_reg_"+mdl+ck1+"_interupt_sync")    | lalign(max_name_len) }} )
);

{% set fst_start_addr=tpl_dict["cross_ck_dict"]["fst_ck_start_addr"] %}
{% set fst_end_addr  =tpl_dict["cross_ck_dict"]["fst_ck_end_addr"]   %}
{% set snd_start_addr=tpl_dict["cross_ck_dict"]["snd_ck_start_addr"] %}
{% set snd_end_addr  =tpl_dict["cross_ck_dict"]["snd_ck_end_addr"]   %}
{% set align_len     =tpl_dict["cross_ck_dict"]["max_len"]           %}
nbl_cif_demux #(
    .CIF_AW             ( {{ aw | lalign(align_len) }} ),
    .CIF_DW             ( {{ dw | lalign(align_len) }} ),
    .DEMUX_NUM          ( {{ 2  | lalign(align_len) }} ),
    .ADDR_STR           ( {{"{"}} {{ fst_start_addr }}, {{ snd_start_addr }} {{"}"}} ),
    .ADDR_END           ( {{"{"}} {{ fst_end_addr }}, {{ snd_end_addr }} {{"}"}} ),
    .REG_OUT            ( {{ 0  | lalign(align_len) }} ),
    .END_OF_PARA_LIST   ( {{ 1  | lalign(align_len) }} )
) U_CIF_DEMUX (
    .i_clk              ( {{ (clk+ck0) | lalign(align_len) }} ),
    .i_rst_n            ( {{ (rst+ck0) | lalign(align_len) }} ),
    .i_cif_req          ( {{ tpl_dict["cross_ck_dict"]["cif_req"]   | lalign(align_len) }} ),
    .i_cif_rw           ( {{ tpl_dict["cross_ck_dict"]["cif_rw"]    | lalign(align_len) }} ),
    .i_cif_addr         ( {{ tpl_dict["cross_ck_dict"]["cif_addr"]  | lalign(align_len) }} ),
    .i_cif_wdata        ( {{ tpl_dict["cross_ck_dict"]["cif_wdata"] | lalign(align_len) }} ),
    .o_cif_ack          ( {{ tpl_dict["cross_ck_dict"]["cif_ack"]   | lalign(align_len) }} ),
    .o_cif_rdata        ( {{ tpl_dict["cross_ck_dict"]["cif_rdata"] | lalign(align_len) }} ),
    .o_cif_demux_req    ( {{"{"}} {{ tpl_dict["cross_ck_dict"]["ck0_req"]   | lalign(align_len) }}, {{ tpl_dict["cross_ck_dict"]["mid_req"]   | lalign(align_len) }} {{"}"}} ),
    .o_cif_demux_rw     ( {{"{"}} {{ tpl_dict["cross_ck_dict"]["ck0_rw"]    | lalign(align_len) }}, {{ tpl_dict["cross_ck_dict"]["mid_rw"]    | lalign(align_len) }} {{"}"}} ),
    .o_cif_demux_addr   ( {{"{"}} {{ tpl_dict["cross_ck_dict"]["ck0_addr"]  | lalign(align_len) }}, {{ tpl_dict["cross_ck_dict"]["mid_addr"]  | lalign(align_len) }} {{"}"}} ),
    .o_cif_demux_wdata  ( {{"{"}} {{ tpl_dict["cross_ck_dict"]["ck0_wdata"] | lalign(align_len) }}, {{ tpl_dict["cross_ck_dict"]["mid_wdata"] | lalign(align_len) }} {{"}"}} ),
    .i_demux_cif_ack    ( {{"{"}} {{ tpl_dict["cross_ck_dict"]["ck0_ack"]   | lalign(align_len) }}, {{ tpl_dict["cross_ck_dict"]["mid_ack"]   | lalign(align_len) }} {{"}"}} ),
    .i_demux_cif_rdata  ( {{"{"}} {{ tpl_dict["cross_ck_dict"]["ck0_rdata"] | lalign(align_len) }}, {{ tpl_dict["cross_ck_dict"]["mid_rdata"] | lalign(align_len) }} {{"}"}} )
);

cif_sync #(
    .CIF_DATA_WIDTH     ( {{ dw | lalign(align_len) }} ),
    .CIF_ADDR_WIDTH     ( {{ aw | lalign(align_len) }} )
) U_CIF_SYNC (
    .rst_n_cif          ( {{ (rst+ck0) | lalign(align_len) }} ),
    .clk_cif            ( {{ (clk+ck0) | lalign(align_len) }} ),
    .rst_n              ( {{ (rst+ck1) | lalign(align_len) }} ),
    .clk                ( {{ (clk+ck1) | lalign(align_len) }} ),
    .cif_req            ( {{ tpl_dict["cross_ck_dict"]["mid_req"]   | lalign(align_len) }} ),
    .cif_rw             ( {{ tpl_dict["cross_ck_dict"]["mid_rw"]    | lalign(align_len) }} ),
    .cif_addr           ( {{ tpl_dict["cross_ck_dict"]["mid_addr"]  | lalign(align_len) }} ),
    .cif_wdata          ( {{ tpl_dict["cross_ck_dict"]["mid_wdata"] | lalign(align_len) }} ),
    .cif_ack            ( {{ tpl_dict["cross_ck_dict"]["mid_ack"]   | lalign(align_len) }} ),
    .cif_rdata          ( {{ tpl_dict["cross_ck_dict"]["mid_rdata"] | lalign(align_len) }} ),
    .cif_sync_req       ( {{ tpl_dict["cross_ck_dict"]["ck1_req"]   | lalign(align_len) }} ),
    .cif_sync_rw        ( {{ tpl_dict["cross_ck_dict"]["ck1_rw"]    | lalign(align_len) }} ),
    .cif_sync_addr      ( {{ tpl_dict["cross_ck_dict"]["ck1_addr"]  | lalign(align_len) }} ),
    .cif_sync_wdata     ( {{ tpl_dict["cross_ck_dict"]["ck1_wdata"] | lalign(align_len) }} ),
    .cif_sync_ack       ( {{ tpl_dict["cross_ck_dict"]["ck1_ack"]   | lalign(align_len) }} ),
    .cif_sync_rdata     ( {{ tpl_dict["cross_ck_dict"]["ck1_rdata"] | lalign(align_len) }} )
);

assign o_reg_{{ mdl }}_interupt = {{ ck0_int }} | {{ ck1_int_sync }};