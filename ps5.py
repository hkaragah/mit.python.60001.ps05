# 6.0001/6.00 Problem Set 5 - RSS Feed Filter
# Name:
# Collaborators:
# Time:

import feedparser
import string
import time
import threading
from project_util import translate_html
from mtTkinter import *
from datetime import datetime
import pytz


# -----------------------------------------------------------------------

# ======================
# Code for retrieving and parsing
# Google and Yahoo News feeds
# Do not change this code
# ======================

def process(url):
    """
    Fetches news items from the rss url and parses them.
    Returns a list of NewsStory-s.
    """
    feed = feedparser.parse(url)
    entries = feed.entries
    ret = []
    for entry in entries:
        guid = entry.guid
        title = translate_html(entry.title)
        link = entry.link
        description = translate_html(entry.description)
        pubdate = translate_html(entry.published)

        try:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %Z")
            pubdate.replace(tzinfo=pytz.timezone("GMT"))
            # pubdate = pubdate.astimezone(pytz.timezone('EST'))
            # pubdate.replace(tzinfo=None)
        except ValueError:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %z")

        newsStory = NewsStory(guid, title, description, link, pubdate)
        ret.append(newsStory)
    return ret

# ======================
# Data structure design
# ======================

# Problem 1


# TODO: NewsStory
class NewsStory(object):

    def __init__(self, guid, title, description, link, pubdate):
        self.guid = guid
        self.title = title
        self.description = description
        self.link = link
        self.pubdate = pubdate

    def get_guid(self):
        return self.guid

    def get_title(self):
        return self.title

    def get_description(self):
        return self.description

    def get_link(self):
        return self.link

    def get_pubdate(self):
        return self.pubdate

# ======================
# Triggers
# ======================


class Trigger(object):
    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        # DO NOT CHANGE THIS!
        raise NotImplementedError

# PHRASE TRIGGERS


# Problem 2
# TODO: PhraseTrigger
class PhraseTrigger(Trigger):

    def __init__(self, phrase):
        self.phrase = self.string_parser(phrase)

    # This 'string_parser' method is used only within the class (class utility method)
    @staticmethod
    def string_parser(text):
        """
        Returns the 'text' while replacing uppercases with lowercase and
        removing extra spaces and punctuations and replacing

        :param text: (String) containing white spaces and punctuations
        :return [String] list of lowercase strings without punctuations
        """
        import string
        text = text.lower()
        parsed_string = ''
        for char in text:
            if char in string.punctuation:
                parsed_string += ' '
            else:
                parsed_string += char
        return parsed_string.split()

    def get_phrase(self):
        return self.phrase

    def is_phrase_in(self, story):
        """
        Return True if story contains the phrase
        :param story: (String)
        :return: Bool, True if story contains the phrase
        """
        # Parsing the story
        story = self.string_parser(story)
        index = 0
        found = False
        for word in self.phrase:
            while index < len(story):
                if word == story[index]:
                    found = True
                    index += 1
                    if word == self.phrase[-1]:
                        return True
                    break
                else:
                    if found:
                        return False
                    else:
                        index += 1
        return False

    def evaluate(self, story):
        return self.is_phrase_in(self, story)


# Problem 3
# TODO: TitleTrigger
class TitleTrigger(PhraseTrigger):
    def __init__(self, phrase):
        PhraseTrigger.__init__(self, phrase)

    def evaluate(self, story):
        return PhraseTrigger.is_phrase_in(self, story.get_title())

# Problem 4
# TODO: DescriptionTrigger
class DescriptionTrigger(PhraseTrigger):
    def __init__(self, phrase):
        PhraseTrigger.__init__(self, phrase)

    def evaluate(self, story):
        return PhraseTrigger.is_phrase_in(self, story.get_description())

# TIME TRIGGERS

# Problem 5
# TODO: TimeTrigger
class TimeTrigger(Trigger):
    def __init__(self, dt_string):
        """
        Convert time from string to a datetime before saving it as an attribute.

        :param dt_string: (String) has to be in EST and in the format of "%d %b %Y %H:%M:%S"
        """
        from datetime import datetime
        temp = datetime.strptime(dt_string, "%d %b %Y %H:%M:%S")
        self.dt = temp.replace(tzinfo=pytz.timezone('EST'))

    def get_datetime(self):
        return self.dt


# Problem 6
# TODO: BeforeTrigger and AfterTrigger
class BeforeTrigger(TimeTrigger):
    def __init__(self, date_time):
        TimeTrigger.__init__(self, date_time)

    def evaluate(self, story):
        """
        :param story: of class "NewsStory"
        :return: True of story publication date is strictly before date_time
        """
        pubdate = story.get_pubdate().replace(tzinfo=self.dt.tzinfo)
        if pubdate < self.dt:
            return True
        else:
            return False


class AfterTrigger(TimeTrigger):
    def __init__(self, date_time):
        TimeTrigger.__init__(self, date_time)

    def evaluate(self, story):
        """
        :param story: of class "NewsStory"
        :return: True of story publication date is strictly after date_time
        """
        pubdate = story.get_pubdate().replace(tzinfo=self.dt.tzinfo)
        if pubdate > self.dt:
            return True
        else:
            return False

# COMPOSITE TRIGGERS

# Problem 7
# TODO: NotTrigger
class NotTrigger(Trigger):
    def __init__(self, trigger):
        self.trigger = trigger

    def get_trigger(self):
        return self.trigger

    def evaluate(self, story):
        return not self.trigger.evaluate(story)

# Problem 8
# TODO: AndTrigger
class AndTrigger(Trigger):
    def __init__(self, trigger1, trigger2):
        self.trigger1 = trigger1
        self.trigger2 = trigger2

    def get_trigger(self):
        return self.trigger1, self.trigger2

    def evaluate(self, story):
        if self.trigger1.evaluate(story) and self.trigger2.evaluate(story):
            return True
        else:
            return False

# Problem 9
# TODO: OrTrigger
class OrTrigger(Trigger):
    def __init__(self, trigger1, trigger2):
        self.trigger1 = trigger1
        self.trigger2 = trigger2

    def get_trigger(self):
        return self.trigger1, self.trigger2

    def evaluate(self, story):
        if self.trigger1.evaluate(story) or self.trigger2.evaluate(story):
            return True
        else:
            return False

# ======================
# Filtering
# ======================

# Problem 10
def filter_stories(stories, triggerlist):
    """
    Takes in a list of NewsStory instances.

    Returns: a list of only the stories for which a trigger in triggerlist fires.
    """
    # TODO: Problem 10
    filtered_stories = []
    for story in stories:
        for trigger in triggerlist:
            if trigger.evaluate(story):
                filtered_stories.append(story)
    return filtered_stories


# ======================
# User-Specified Triggers
# ======================


# Problem 11
def read_trigger_config(filename):
    """
    filename: the name of a trigger configuration file

    Returns: a list of trigger objects specified by the trigger configuration
        file.
    """
    # We give you the code to read in the file and eliminate blank lines and
    # comments. You don't need to know how it works for now!
    trigger_file = open(filename, 'r')
    lines = []
    for line in trigger_file:
        line = line.rstrip()
        if not (len(line) == 0 or line.startswith('//')):
            lines.append(line)


    # TODO: Problem 11
    # line is the list of lines that you need to parse and for which you need
    # to build triggers

    triggers = {}
    lines_copy = lines[:]

    for line in lines_copy:

        split_line = line.lower().split(',')
        # print(line)

        if split_line[1] == "title":
            triggers[split_line[0]] = TitleTrigger(split_line[2])
            lines.remove(line)
        elif split_line[1] == "description":
            triggers[split_line[0]] = DescriptionTrigger(split_line[2])
            lines.remove(line)
        elif split_line[1] == "after":
            triggers[split_line[0]] = AfterTrigger(split_line[2])
            lines.remove(line)
        elif split_line[1] == "before":
            triggers[split_line[0]] = BeforeTrigger(split_line[2])
            lines.remove(line)

    lines_copy = lines[:]

    for line in lines_copy:

        split_line = line.lower().split(',')

        if split_line[1] == "not":
            triggers[split_line[0]] = NotTrigger(split_line[2])
            lines.remove(line)
        elif split_line[1] == "or":
            try:
                triggers[split_line[0]] = OrTrigger(triggers[split_line[2]], triggers[split_line[3]])
                lines.remove(line)
            except KeyError:
                lines.remove(line)
                print("Warning in OrTrigger: trigger", split_line[2], "or", split_line[3], "does not exist.")
                print("Hence, trigger", split_line[0], "was not created.\n")
        elif split_line[1] == "and":
            try:
                triggers[split_line[0]] = AndTrigger(triggers[split_line[2]], triggers[split_line[3]])
                lines.remove(line)
            except KeyError:
                lines.remove(line)
                print("Warning in AndTrigger: trigger", split_line[2], "or", split_line[3], "does not exist.")
                print("Hence, trigger", split_line[0], "was not created.\n")

    added_triggers = []

    for line in lines:

        line = line.lower()
        split_line = line.split(',')

        if split_line[0] == "add":
            for index in range(1, len(split_line)):
                try:
                    added_triggers.append(triggers[split_line[index]])
                except KeyError:
                    print("Warning: trigger", split_line[index], "does not exist")

    return added_triggers


SLEEPTIME = 120  # seconds -- how often we poll


def main_thread(master):
    # A sample trigger list - you might need to change the phrases to correspond
    # to what is currently in the news
    try:
        # t1 = TitleTrigger("coronavirus")
        # t2 = DescriptionTrigger("Trump")
        # t3 = DescriptionTrigger("pandemic")
        # t4 = AndTrigger(t2, t3)
        # triggerlist = [t1, t4]

        # Problem 11
        # TODO: After implementing read_trigger_config, uncomment this line
        triggerlist = read_trigger_config('triggers.txt')


        # HELPER CODE - you don't need to understand this!
        # Draws the popup window that displays the filtered stories
        # Retrieves and filters the stories from the RSS feeds
        frame = Frame(master)
        frame.pack(side=BOTTOM)
        scrollbar = Scrollbar(master)
        scrollbar.pack(side=RIGHT, fill=Y)

        t = "BBC & Wall Street Journal's Top News"
        title = StringVar()
        title.set(t)
        ttl = Label(master, textvariable=title, font=("Helvetica", 18))
        ttl.pack(side=TOP)
        cont = Text(master, font=("Helvetica", 14), yscrollcommand=scrollbar.set)
        cont.pack(side=BOTTOM)
        cont.tag_config("title", justify='center')
        button = Button(frame, text="Exit", command=root.destroy)
        button.pack(side=BOTTOM)
        guidShown = []

        def get_cont(newstory):
            if newstory.get_guid() not in guidShown:
                cont.insert(END, newstory.get_title()+"\n", "title")
                cont.insert(END, "\n---------------------------------------------------------------\n", "title")
                cont.insert(END, newstory.get_description())
                cont.insert(END, "\n*********************************************************************\n", "title")
                guidShown.append(newstory.get_guid())

        while True:

            print("Polling . . .", end=' ')
            # Get stories from Google's Top Stories RSS news feed
            # google_rss_url = "http://news.google.com/news?output=rss" # NOT WORKING
            # yahoo_rss_url = "http://news.yahoo.com/rss/topstories" # NOT WORKING
            bbc_rss_url = "http://feeds.bbci.co.uk/news/rss.xml#"
            stories = process(bbc_rss_url)

            # Get stories from Wall Street Journal's RSS news feed
            wsj_rss_url = "https://feeds.a.dj.com/rss/RSSWorldNews.xml"
            stories.extend(process(wsj_rss_url))

            stories = filter_stories(stories, triggerlist)

            list(map(get_cont, stories))
            scrollbar.config(command=cont.yview)

            print("Sleeping...")
            time.sleep(SLEEPTIME)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    root = Tk()
    root.title("Some RSS parser")
    t = threading.Thread(target=main_thread, args=(root,))
    t.start()
    root.mainloop()
