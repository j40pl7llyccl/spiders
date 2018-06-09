

def is_element_exist(driver,css):
    s = driver.find_elements_by_css_selector(css_selector=css)
    if len(s) == 0:
        return False
    elif len(s) == 1:
        return True
    else:
        return False