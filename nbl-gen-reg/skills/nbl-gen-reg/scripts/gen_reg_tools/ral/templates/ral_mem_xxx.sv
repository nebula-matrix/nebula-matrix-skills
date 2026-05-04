{% for tbl_dict in tpl_dict.get("subpart") %}
{% set bn = tbl_dict.get("bn") %}
{% set tn = tbl_dict.get("name") %}
class ral_mem_{{ bn }}_{{ tn }} extends project_mem;
   function new(string name = "{{ bn }}_{{ tn }}");
      super.new(name, `UVM_REG_ADDR_WIDTH'd{{ tbl_dict["depth"] }}, {{ tbl_dict["width"] }}, "RW", build_coverage(UVM_NO_COVERAGE));
   endfunction
   virtual function void build();
        this.set_mask(`UVM_REG_DATA_WIDTH'h{{ tbl_dict["rmask"] }}, `UVM_REG_DATA_WIDTH'h{{ tbl_dict["wmask"] }});
        this.set_reset(`UVM_REG_DATA_WIDTH'h{{ tbl_dict["reset"] }});
   endfunction: build

   `uvm_object_utils(ral_{{ bn }}_{{ tn }})

endclass : ral_mem_{{ bn }}_{{ tn }}

{% endfor %}
