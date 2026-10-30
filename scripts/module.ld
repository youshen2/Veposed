SECTIONS {
    .text : ALIGN(4) { *(.text .text.*) }
    .rodata : ALIGN(4) { *(.rodata .rodata.*) }
    .data : ALIGN(4) { *(.data .data.*) }
    .bss : ALIGN(4) { *(.bss .bss.* COMMON) }
    .init_array : ALIGN(4) { KEEP(*(SORT_BY_INIT_PRIORITY(.init_array.*))) KEEP(*(.init_array)) }
    .fini_array : ALIGN(4) { KEEP(*(SORT_BY_INIT_PRIORITY(.fini_array.*))) KEEP(*(.fini_array)) }
    /DISCARD/ : { *(.ARM.exidx* .ARM.extab* .eh_frame* .comment) }
}
