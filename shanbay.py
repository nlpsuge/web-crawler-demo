import sys

from lxml import etree
from selenium import webdriver

# https://blog.csdn.net/u013322949/article/details/60376411
reload(sys)
sys.setdefaultencoding("utf-8")


class shanbay:

    def __init__(self):
        self.firefox_binary = 'the_path_of_firefox_file'
        self.executable_path = 'the_path_of_geckodriver_file'
        self.my_driver = None
        self.url = 'https://www.shanbay.com/wordbook/86569/'
        self.file_path = 'shanbay.txt'
        self.run_firefox()
        self.get()

    def run_firefox(self):
        print('opening browser')

        # set open link in current tab
        options = webdriver.FirefoxOptions()
        options.set_preference('browser.link.open_newwindow', 1)
        options.set_preference('browser.tabs.loadDivertedInBackground', False)
        # set headless
        # options.headless = True

        self.my_driver = webdriver.Firefox(executable_path=self.executable_path,
                                     firefox_binary=self.firefox_binary,
                                     firefox_options=options)

    def get(self):
        out_file = open(self.file_path, 'wb')

        # self.my_driver.execute_script('window.open("%s")' % self.url)
        self.my_driver.get(self.url)

        word_list = self.my_driver.find_elements_by_xpath(".//*[@id='wordlist-']/div[1]/table/tbody/tr/td[1]/a")

        print('word_list: ' + len(word_list))

        for i_wl in range(len(word_list)):
            new_wl = self.my_driver.find_elements_by_xpath(".//*[@id='wordlist-']/div[1]/table/tbody/tr/td[1]/a")
            href = new_wl[i_wl].get_attribute('href')
            self.my_driver.get(href)
            # retrieve words in the first one page
            self.retrieve_text(out_file)

            pagination = self.my_driver.find_elements_by_xpath('.//*[@id="pagination"]/div/ul/li/a')

            page_num = pagination[len(pagination) - 2].get_attribute('data-page')

            print('Total: ' + page_num)

            # start at the second page
            for i in range(1, int(page_num)):
                self.my_driver.get(href + '?page=%d' % (i + 1))
                self.retrieve_text(out_file)

            # back forward to the start page
            self.my_driver.get(self.url)

    # retrieve words from current page
    def retrieve_text(self, out_file):
        trs = self.my_driver.find_elements_by_xpath('html/body/div[3]/div/div[1]/div[2]/div/table/tbody/tr')

        text = ''
        for i_trs in range(len(trs)):
            tr = trs[i_trs]
            html_tr = tr.get_attribute('innerHTML')
            # https://lxml.de/tutorial.html#using-xpath-to-find-text
            content = etree.HTML(html_tr)
            word_td_strong = content.xpath('//td/strong')[0]
            meaning_td = content.xpath('//td[@class="span10"]')[0]
            word = word_td_strong.text

            # http://stackoverflow.com/questions/4843173/ddg#4843178
            try:
                meaning = unicode.replace(unicode.strip(meaning_td.text), '\n', ' ')
            except:
                import traceback
                print(traceback.format_exc())
                meaning = str.replace(str.strip(meaning_td.text), '\n', ' ')

            # Append '\n' to every text from table
            text = text + (word + '\t' + meaning) + '\n'

        out_file.write(text)
        out_file.flush()


shanbay()

