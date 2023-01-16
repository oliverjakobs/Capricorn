# Theme dark
namespace eval ttk::theme::dark {
    
    # Widget colors
    variable colors
    array set colors {
        -foreground     "#e1e4e8"
        -background     "#454545"
        -background2    "#2f2f2f"
        -fg_text        "#000000"
        -bg_text        "#f1f1f1"
        -fg_title       "#b392f0"
        -scrollbar      "#6f6f6f"
    }

    # Create a new ttk::style
    ttk::style theme create dark -parent default -settings {
        # Configure basic style settings
        ttk::style configure . \
            -background $colors(-background) \
            -foreground $colors(-foreground) \
            -font {"Courier New" 10}

        # WIDGET LAYOUTS

        # scrollbar
        ttk::style layout Vertical.TScrollbar {
            Vertical.Scrollbar.trough -sticky ns -children {
                Vertical.Scrollbar.thumb -expand true
            }
        }

        # Style elements
        
        # Text 
        ttk::style configure TText \
            -background $colors(-bg_text) \
            -foreground $colors(-fg_text) \
            -insertbackground $colors(-fg_text) \
            -padx 16 -pady 16 \
            -borderwidth 1 -relief solid \

        ttk::style configure Title.TText \
            -foreground $colors(-fg_title) \
            -font {"Courier New" 24 bold}

        ttk::style configure TFrame -background $colors(-background)

        # Statusbar
        ttk::style configure Statusbar.TFrame -background $colors(-background2)
        ttk::style configure Statusbar.TLabel -background $colors(-background2)

        # scrollbar
        ttk::style configure TScrollbar \
            -troughcolor $colors(-background) -troughrelief flat \
            -background $colors(-scrollbar) -relief flat
    }
}

variable version 0.1
package provide ttk::theme::dark $version

