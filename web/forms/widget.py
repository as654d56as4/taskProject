from django.forms import RadioSelect


# 自定义一个插件
class ColorRadioSelect(RadioSelect):
    template_name = 'widgets/color_radio/radio.html'
    option_template_name = 'widgets/color_radio/radio_option.html'
