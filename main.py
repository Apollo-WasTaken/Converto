import ctypes
import os
import sys
import requests
import customtkinter as ctk


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)


# weird scaling issues on windows
if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except:
            pass


# font loading
FONT_PATH = resource_path(os.path.join("Anthropic Sans-fontiko", "AnthropicSans-Display-Bold-Static.otf"))

if sys.platform == "win32" and os.path.exists(FONT_PATH):
    try:
        ctypes.windll.gdi32.AddFontResourceExW(FONT_PATH, 0x10, 0)
    except Exception as e:
        print(f"Error loading custom font: {e}")


# theme colours
BG_MAIN      = "#0C0E22"
BG_CARD      = "#0F1028"
BG_WIDGET    = "#161840"
BORDER       = "#252560"
TEXT         = "#EAE8F6"
TEXT_MUTED   = "#9488CC"
ACCENT       = "#6448E4"
ACCENT_HOVER = "#7860F8"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Converto")
        self.geometry("1280x800")
        try:
            self.iconbitmap(resource_path("icon.ico"))
        except Exception:
            pass
        self.configure(fg_color=BG_MAIN)
        self.resizable(False, False)
        
        ctk.deactivate_automatic_dpi_awareness()
        ctk.set_widget_scaling(1.0)
        ctk.set_window_scaling(1.0)

        self.FONT_TITLE = ("Anthropic Sans Display", 56, "bold")
        self.FONT_SUBTITLE = ("Anthropic Sans Display", 32, "bold")
        self.FONT_RESULT = ("Anthropic Sans Display", 32, "bold")
        self.FONT_LABEL = ("Anthropic Sans Display", 40, "bold")
        self.FONT_COMBOBOX_LABEL = ("Anthropic Sans Display", 32, "bold")
        self.FONT_BUTTON = ("Anthropic Sans Display", 36, "bold")
        self.FONT_ENTRY = ("Anthropic Sans Display", 36)
        
        # initialize resources and UI components
        self.initialise_data()
        self._setup_widgets()
        self._center_window()

        # set default UI selections
        self.combobox_unit.set("Length")
        self.on_unit_change()

    def _center_window(self):
        self.update_idletasks()
        width, height = 1280, 800
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.minsize(width, height)
        self.maxsize(width, height)

    #  Data & Conversion Setup 
    def initialise_data(self):
        # Lists of units per category for Combobox options
        self.categories = {
            "Currency": ["EUR", "USD", "GBP", "CHF", "JPY", "CAD", "AUD"],
            "Length": ["Meter(m)", "Millimeter(mm)", "Centimeter(cm)", "Kilometer(km)", "Foot(ft)", "Inch(in)", "Mile(mi)", "Yard(yd)"],
            "Mass": ["Gram(g)", "Kilogram(kg)", "Milligram(mg)", "Pound(lb)", "Ounce(oz)"],
            "Temperature": ["Celsius(°C)", "Fahrenheit(°F)", "Kelvin(K)"],
            "Volume": ["Liter(L)", "Milliliter(mL)", "Gallon(gal)", "Quart(qt)", "Pint(pt)"],
            "Area": ["Square Meter(m²)", "Square Millimeter(mm²)", "Square Centimeter(cm²)", "Square Kilometer(km²)", "Square Foot(ft²)", "Square Inch(in²)", "Square Mile(mi²)", "Square Yard(yd²)"],
            "Time": ["Second(s)", "Millisecond(ms)", "Minute(min)", "Hour(h)", "Day(d)", "Week(wk)", "Month(mo)", "Year(yr)", "Decade(dc)", "Century(c)", "Millennium(ml)"],
            "Digital Storage": ["Bit(b)", "Kilobit(kb)", "Megabit(Mb)", "Gigabit(Gb)", "Terabit(Tb)", "Petabit(Pb)", "Exabit(Eb)", "Zettabit(Zb)", "Yottabit(Yb)", "Byte(B)", "Kilobyte(KB)", "Megabyte(MB)", "Gigabyte(GB)", "Terabyte(TB)", "Petabyte(PB)", "Exabyte(EB)", "Zettabyte(ZB)", "Yottabyte(YB)"],
            "Data Transfer Speed": ["Bit per second(bps)", "Kilobit per second(kbps)", "Megabit per second(Mbps)", "Gigabit per second(Gbps)", "Terabit per second(Tbps)", "Petabit per second(Pbps)", "Exabit per second(Ebps)", "Zettabit per second(Zbps)", "Yottabit per second(Ybps)"],
            "Pressure": ["Pascal(Pa)", "Kilopascal(kPa)", "Megapascal(MPa)", "Hectopascal(hPa)", "Millibar(mbar)", "Bar(bar)", "Atmosphere(atm)", "Millimeter of mercury(mmHg)", "Inch of mercury(inHg)"],
            "Power": ["Watt(W)", "Kilowatt(kW)", "Megawatt(MW)", "Gigawatt(GW)", "Terawatt(TW)", "Petawatt(PW)", "Exawatt(EW)", "Zettawatt(ZW)", "Yottawatt(YW)"],
            "Energy": ["Joule(J)", "Kilojoule(kJ)", "Megajoule(MJ)", "Gigajoule(GJ)", "Terajoule(TJ)", "Petajoule(PJ)", "Exajoule(EJ)", "Zettajoule(ZJ)", "Yottajoule(YJ)"],
            "Speed": ["km/h", "km/min", "km/s", "m/h", "m/min", "m/s", "mile/h", "mile/min", "mile/s"]
        }

        # conversion ratios
        self.length_units = {
            "Meter(m)": 1.0, "Millimeter(mm)": 0.001, "Centimeter(cm)": 0.01,
            "Kilometer(km)": 1000.0, "Foot(ft)": 0.3048, "Inch(in)": 0.0254,
            "Mile(mi)": 1609.34, "Yard(yd)": 0.9144
        }
        self.mass_units = {
            "Gram(g)": 1.0, "Kilogram(kg)": 1000.0, "Milligram(mg)": 0.001,
            "Pound(lb)": 453.592, "Ounce(oz)": 28.3495
        }
        self.time_units = {
            "Second(s)": 1.0, "Millisecond(ms)": 0.001, "Minute(min)": 60.0,
            "Hour(h)": 3600.0, "Day(d)": 86400.0, "Week(wk)": 604800.0,
            "Month(mo)": 2592000.0, "Year(yr)": 31536000.0, "Decade(dc)": 315360000.0,
            "Century(c)": 3153600000.0, "Millennium(ml)": 31536000000.0
        }
        self.volume_units = {
            "Liter(L)": 1.0, "Milliliter(mL)": 0.001, "Gallon(gal)": 3.78541,
            "Quart(qt)": 0.946353, "Pint(pt)": 0.473176
        }
        self.area_units = {
            "Square Meter(m²)": 1.0, "Square Millimeter(mm²)": 0.000001, "Square Centimeter(cm²)": 0.0001,
            "Square Kilometer(km²)": 1000000.0, "Square Foot(ft²)": 0.092903, "Square Inch(in²)": 0.00064516,
            "Square Mile(mi²)": 2589990.0, "Square Yard(yd²)": 0.836127
        }
        self.data_transfer_units = {
            "Bit per second(bps)": 1.0, "Kilobit per second(kbps)": 1000.0, "Megabit per second(Mbps)": 1000000.0,
            "Gigabit per second(Gbps)": 1000000000.0, "Terabit per second(Tbps)": 1000000000000.0,
            "Petabit per second(Pbps)": 1000000000000000.0, "Exabit per second(Ebps)": 1000000000000000000.0,
            "Zettabit per second(Zbps)": 1e21, "Yottabit per second(Ybps)": 1e24
        }
        self.speed_units = {
            "km/h": 1.0, "km/min": 60.0, "km/s": 3600.0,
            "m/h": 0.001, "m/min": 0.06, "m/s": 3.6,
            "mile/h": 1.60934, "mile/min": 96.5597, "mile/s": 5793.58
        }
        self.digital_storage_units = {
            "Bit(b)": 1.0, "Kilobit(kb)": 1000.0, "Megabit(Mb)": 1000000.0,
            "Gigabit(Gb)": 1000000000.0, "Terabit(Tb)": 1000000000000.0,
            "Petabit(Pb)": 1000000000000000.0, "Exabit(Eb)": 1000000000000000000.0,
            "Zettabit(Zb)": 1e21, "Yottabit(Yb)": 1e24,
            "Byte(B)": 8.0, "Kilobyte(KB)": 8000.0, "Megabyte(MB)": 8000000.0,
            "Gigabyte(GB)": 8000000000.0, "Terabyte(TB)": 8000000000000.0,
            "Petabyte(PB)": 8000000000000000.0, "Exabyte(EB)": 8000000000000000000.0,
            "Zettabyte(ZB)": 8e21, "Yottabyte(YB)": 8e24
        }
        self.energy_units = {
            "Joule(J)": 1.0, "Kilojoule(kJ)": 1000.0, "Megajoule(MJ)": 1000000.0,
            "Gigajoule(GJ)": 1000000000.0, "Terajoule(TJ)": 1000000000000.0,
            "Petajoule(PJ)": 1000000000000000.0, "Exajoule(EJ)": 1000000000000000000.0,
            "Zettajoule(ZJ)": 1e21, "Yottajoule(YJ)": 1e24
        }
        self.power_units = {
            "Watt(W)": 1.0, "Kilowatt(kW)": 1000.0, "Megawatt(MW)": 1000000.0,
            "Gigawatt(GW)": 1000000000.0, "Terawatt(TW)": 1000000000000.0,
            "Petawatt(PW)": 1000000000000000.0, "Exawatt(EW)": 1000000000000000000.0,
            "Zettawatt(ZW)": 1e21, "Yottawatt(YW)": 1e24
        }
        self.pressure_units = {
            "Pascal(Pa)": 1.0, "Kilopascal(kPa)": 1000.0, "Megapascal(MPa)": 1000000.0,
            "Hectopascal(hPa)": 100.0, "Millibar(mbar)": 100.0, "Bar(bar)": 100000.0,
            "Atmosphere(atm)": 101325.0, "Millimeter of mercury(mmHg)": 133.322,
            "Inch of mercury(inHg)": 3386.38867
        }

    #  Widgets Setup 
    def _setup_widgets(self):
        # Header title
        self.header = ctk.CTkLabel(self, text="Converto", text_color=TEXT, font=self.FONT_TITLE, fg_color="transparent")
        self.header.place(relx=0.5, y=50, anchor="center")

        # Subtitle
        self.secondary_header = ctk.CTkLabel(self, text="Unit Converter", text_color=TEXT_MUTED, font=self.FONT_SUBTITLE, fg_color="transparent")
        self.secondary_header.place(relx=0.5, y=95, anchor="center")

        # Main background card
        self.main_frame = ctk.CTkFrame(self, fg_color=BG_CARD, border_color=BORDER, border_width=1, corner_radius=12, width=600, height=530)
        self.main_frame.place(relx=0.5, y=200, anchor="n")

        # Labels
        self.label_unit = ctk.CTkLabel(self.main_frame, text="Unit", text_color=TEXT_MUTED, font=self.FONT_LABEL, anchor="w", fg_color="transparent")
        self.label_unit.place(x=40, y=40)

        self.label_from = ctk.CTkLabel(self.main_frame, text="From", text_color=TEXT_MUTED, font=self.FONT_LABEL, anchor="w", fg_color="transparent")
        self.label_from.place(x=40, y=100)

        self.label_to = ctk.CTkLabel(self.main_frame, text="To", text_color=TEXT_MUTED, font=self.FONT_LABEL, anchor="w", fg_color="transparent")
        self.label_to.place(x=40, y=160)

        self.label_value = ctk.CTkLabel(self.main_frame, text="Value", text_color=TEXT_MUTED, font=self.FONT_LABEL, anchor="w", fg_color="transparent")
        self.label_value.place(x=40, y=220)

        # unit_values
        unit_values = ["Currency", "Length", "Mass", "Volume", "Temperature", "Energy", "Power", "Pressure", "Speed", "Digital Storage", "Data Transfer Speed"]

        # unit_values combobox
        self.combobox_unit = ctk.CTkComboBox(
            self.main_frame, values=unit_values, fg_color=BG_MAIN, border_color=BORDER, width=350, height=45,
            font=self.FONT_COMBOBOX_LABEL, button_color=ACCENT, button_hover_color=ACCENT_HOVER,
            dropdown_font=self.FONT_COMBOBOX_LABEL, text_color=TEXT, dropdown_fg_color=BG_MAIN,
            dropdown_hover_color=ACCENT, dropdown_text_color=TEXT, hover=True, command=self.on_unit_change
        ) 
        self.combobox_unit.place(x=210, y=40)

        self.combobox_from = ctk.CTkComboBox(
            self.main_frame, values=[], fg_color=BG_MAIN, border_color=BORDER, width=350, height=45,
            font=self.FONT_COMBOBOX_LABEL, button_color=ACCENT, button_hover_color=ACCENT_HOVER,
            dropdown_font=self.FONT_COMBOBOX_LABEL, text_color=TEXT, dropdown_fg_color=BG_MAIN,
            dropdown_hover_color=ACCENT, dropdown_text_color=TEXT, hover=True
        ) 
        self.combobox_from.place(x=210, y=100)

        self.combobox_to = ctk.CTkComboBox(
            self.main_frame, values=[], fg_color=BG_MAIN, border_color=BORDER, width=350, height=45,
            font=self.FONT_COMBOBOX_LABEL, button_color=ACCENT, button_hover_color=ACCENT_HOVER,
            dropdown_font=self.FONT_COMBOBOX_LABEL, text_color=TEXT, dropdown_fg_color=BG_MAIN,
            dropdown_hover_color=ACCENT, dropdown_text_color=TEXT, hover=True
        ) 
        self.combobox_to.place(x=210, y=160)

        # value entry
        self.entry_value = ctk.CTkEntry(
            self.main_frame, placeholder_text="Enter value...", fg_color=BG_WIDGET, border_color=BORDER,
            text_color=TEXT, corner_radius=8, font=self.FONT_ENTRY, width=350, height=50,
            border_width=1, placeholder_text_color=TEXT_MUTED
        )
        self.entry_value.place(x=210, y=220)

        # convert button
        self.button_convert = ctk.CTkButton(
            self.main_frame, text="Convert", fg_color=ACCENT, text_color=TEXT, corner_radius=12,
            hover_color=ACCENT_HOVER, font=self.FONT_BUTTON, anchor="center", width=520, height=60,
            command=self.perform_conversion
        )
        self.button_convert.place(x=40, y=285)

        # result frame
        self.frame_result = ctk.CTkFrame(self.main_frame, fg_color=BG_WIDGET, border_color=BORDER, border_width=1, corner_radius=12, width=520, height=150)
        self.frame_result.place(x=40, y=360)

        self.label_result = ctk.CTkLabel(self.frame_result, text="Result:", text_color=TEXT_MUTED, font=self.FONT_RESULT, anchor="w", fg_color="transparent")
        self.label_result.place(x=30, y=15)

        self.result = ctk.CTkLabel(self.frame_result, text="—", text_color=TEXT, font=self.FONT_RESULT, anchor="w", fg_color="transparent")
        self.result.place(x=30, y=65)

    #  Event Callbacks
    def on_unit_change(self, event=None):
        category = self.combobox_unit.get()
        units = self.categories.get(category, [])
        
        # Reload matching list values to comboboxes
        self.combobox_from.configure(values=units)
        self.combobox_to.configure(values=units)
        
        # Populate defaults
        if units:
            self.combobox_from.set(units[0])
            self.combobox_to.set(units[1] if len(units) > 1 else units[0])

    #  Calculation Logic
    def perform_conversion(self):
        try:
            val_str = self.entry_value.get().strip()
            if not val_str:
                self.result.configure(text="Please enter a value")
                return
            amount = float(val_str)
        except ValueError:
            self.result.configure(text="Invalid number format")
            return

        category = self.combobox_unit.get()
        from_unit = self.combobox_from.get()
        to_unit = self.combobox_to.get()

        if from_unit == to_unit:
            self.show_output(amount)
            return


        if category == "Currency":
            try:
                res = self.convert_currency(amount, from_unit, to_unit)
                self.show_output(res)
            except Exception:
                self.result.configure(text="API connection failed")
            return

        if category == "Temperature":
            res = self.convert_temperature(amount, from_unit, to_unit)
            self.show_output(res)
            return

        unit_dictionary_map = {
            "Length": self.length_units,
            "Mass": self.mass_units,
            "Volume": self.volume_units,
            "Area": self.area_units,
            "Time": self.time_units,
            "Digital Storage": self.digital_storage_units,
            "Data Transfer Speed": self.data_transfer_units,
            "Pressure": self.pressure_units,
            "Power": self.power_units,
            "Energy": self.energy_units,
            "Speed": self.speed_units
        }

        unit_dict = unit_dictionary_map.get(category)
        if unit_dict and from_unit in unit_dict and to_unit in unit_dict:
            res = self.convert(amount, from_unit, to_unit, unit_dict)
            self.show_output(res)
        else:
            self.result.configure(text="Unsupported conversion")

    def convert(self, amount, from_unit, to_unit, unit_dict):
        return amount * (unit_dict[from_unit] / unit_dict[to_unit])

    def convert_currency(self, amount, from_currency, to_currency):
        url = f"https://api.frankfurter.app/latest?amount={amount}&from={from_currency}&to={to_currency}"
        response = requests.get(url, timeout=200)
        response.raise_for_status()
        data = response.json()
        return data["rates"][to_currency]

    def convert_temperature(self, amount, from_unit, to_unit):
        def parse_symbol(unit):
            if "Celsius" in unit: return "C"
            if "Fahrenheit" in unit: return "F"
            if "Kelvin" in unit: return "K"
            return "C"

        from_temp, to_temp = parse_symbol(from_unit), parse_symbol(to_unit)
        if from_temp == to_temp:
            return amount

        # Convert to Celsius base
        if from_temp == "F":
            celsius = (amount - 32) * 5/9
        elif from_temp == "K":
            celsius = amount - 273.15
        else:
            celsius = amount

        # Convert from Celsius base to target
        if to_temp == "F":
            return (celsius * 9/5) + 32
        elif to_temp == "K":
            return celsius + 273.15
        return celsius

    def show_output(self, value):
        # Format the result nicely (using scientific notation for extremely large or small numbers)
        if value == 0:
            formatted = "0"
        elif abs(value) < 1e-4 or abs(value) > 1e9:
            formatted = f"{value:.4e}"
        else:
            formatted = f"{value:.4f}".rstrip('0').rstrip('.')
        self.result.configure(text=formatted)

# mainloop
def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()