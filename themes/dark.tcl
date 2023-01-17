# Theme dark
namespace eval ttk::theme::dark {
    # Style colors
    array set colors {
        -fg_main    "#e1e4e8"
        -bg_main    "#454545"
        -bg_status  "#2f2f2f"
        -fg_text    "#000000"
        -bg_text    "#f1f1f1"
        -fg_title   "#b392f0"
        -scrollbar  "#6f6f6f"
    }

    set base_font {"Courier New" 10}
    set title_font {"Courier New" 24 bold}

    # Create style
    ttk::style theme create dark -parent default -settings {
        # Basic style settings
        ttk::style configure . \
            -background $colors(-bg_main) \
            -foreground $colors(-fg_main) \
            -font $base_font

        # Scrollbar
        ttk::style layout Vertical.TScrollbar {
            Vertical.Scrollbar.trough -sticky ns -children {
                Vertical.Scrollbar.thumb -expand true
            }
        }

        ttk::style configure TScrollbar \
            -troughcolor $colors(-bg_main) -troughrelief flat \
            -background $colors(-scrollbar) -relief flat
        
        # Text 
        ttk::style configure TText \
            -background $colors(-bg_text) \
            -foreground $colors(-fg_text) \
            -insertbackground $colors(-fg_text) \
            -padx 16 -pady 16 \
            -borderwidth 1 -relief solid \

        ttk::style configure Title.TText \
            -foreground $colors(-fg_title) \
            -font $title_font

        # Statusbar
        ttk::style configure Statusbar.TFrame -background $colors(-bg_status)
        ttk::style configure Statusbar.TLabel -background $colors(-bg_status)
    }
}