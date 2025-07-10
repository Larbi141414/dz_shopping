
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
import subprocess, os

class VulnScanner(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=10)

        # Default language English
        self.lang = 'en'

        # URL input
        self.add_widget(Label(text=self._('Target URL:')))
        self.url_input = TextInput(hint_text="example.com", multiline=False)
        self.add_widget(self.url_input)

        # Language switch
        self.lang_spinner = Spinner(
            text='English',
            values=('English', 'العربية'),
            size_hint=(1, None), height=44
        )
        self.lang_spinner.bind(text=self.set_lang)
        self.add_widget(self.lang_spinner)

        # Tool checkboxes
        self.tools_cb = {}
        self.tools = ['nmap', 'sqlmap', 'whatweb', 'nikto']
        default_active = {'nmap', 'whatweb'}
        for tool in self.tools:
            box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            cb = CheckBox(active=(tool in default_active))
            self.tools_cb[tool] = cb
            box.add_widget(cb)
            box.add_widget(Label(text=tool.upper()))
            self.add_widget(box)

        # Run button
        self.run_btn = Button(text=self._('Run Scan'), size_hint=(1, None), height=50)
        self.run_btn.bind(on_press=self.run_scan)
        self.add_widget(self.run_btn)

        # Results output
        self.output = TextInput(readonly=True, size_hint=(1, 2),
                                background_color=(0,0,0,1), foreground_color=(0,1,0,1))
        self.add_widget(self.output)

    def _(self, text):
        translations = {
            'Target URL:': {'ar': 'رابط الموقع:'},
            'Run Scan': {'ar': 'بدء الفحص'},
            'Please enter target URL': {'ar': 'يرجى إدخال الرابط'},
            'Scanning...': {'ar': 'جاري الفحص...'}
        }
        if self.lang == 'ar':
            return translations.get(text, {}).get('ar', text)
        return text

    def set_lang(self, spinner, value):
        self.lang = 'ar' if value == 'العربية' else 'en'
        # Update dynamic labels
        self.run_btn.text = self._('Run Scan')
        # Note: For brevity, static labels unchanged

    def run_scan(self, *_):
        target = self.url_input.text.strip()
        if not target:
            self.popup(self._('Please enter target URL'))
            return
        self.output.text = self._('Scanning...')

        cmds = []
        for tool, cb in self.tools_cb.items():
            if cb.active:
                if tool == 'nmap':
                    cmds.append(f"nmap -T4 -F {target}")
                elif tool == 'sqlmap':
                    cmds.append(f"sqlmap -u {target} --batch --level=1")
                elif tool == 'whatweb':
                    cmds.append(f"whatweb {target}")
                elif tool == 'nikto':
                    cmds.append(f"nikto -h {target}")

        results = ""
        for cmd in cmds:
            results += f"\n$ {cmd}\n"
            try:
                results += subprocess.getoutput(cmd) + "\n"
            except Exception as e:
                results += str(e) + "\n"
        self.output.text = results

        # Save report
        report_path = os.path.join(os.path.expanduser("~"), "vuln_report.txt")
        with open(report_path, "w") as f:
            f.write(results)

    def popup(self, msg):
        Popup(title='Info', content=Label(text=msg),
              size_hint=(None,None), size=(300,200)).open()

class WebScannerApp(App):
    def build(self):
        return VulnScanner()

if __name__ == '__main__':
    WebScannerApp().run()
