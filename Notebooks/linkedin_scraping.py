# import web driver
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from Login_info import user as user1, password as pass1
import time
import math
import pandas as pd


def Login(wd, user, password):
    # locate email form by_class_name
    wd.find_element_by_id('session_key').send_keys(user)
    time.sleep(1)

    # locate password form by_class_name
    wd.find_element_by_id('session_password').send_keys(password)

    # locate submit button by_class_name
    wd.find_element_by_class_name('sign-in-form__submit-button').click()
    time.sleep(1)


def Search_company(wd, company_name):
    # Search bar
    search = wd.find_element_by_class_name(
        'search-global-typeahead__input.always-show-placeholder')

    # Write company name
    search.send_keys(company_name)

    # Wait
    time.sleep(2)

    search.send_keys(Keys.ENTER)

    time.sleep(2)


def Posts_pagination(wd, keywords):
    time.sleep(2)

    # Get number of total posts
    keywords_url = keywords.replace(' ', '%20')
    wd.get(
        f'https://www.linkedin.com/search/results/content/?keywords={keywords_url}&origin=SWITCH_SEARCH_VERTICAL')
    time.sleep(3)
    amount_of_posts = int(wd.find_element_by_class_name(
        'pb2.t-black--light.t-14').text.split(' ')[0])
    number_of_pages = math.ceil(amount_of_posts/10)

    # String to look
    href = 'https://www.linkedin.com/feed/update/urn:li:activity:'
    posts = {}

    # For each page
    # for j in range(number_of_pages)
    for j in range(number_of_pages):
        wd.get(
            f'https://www.linkedin.com/search/results/content/?keywords=Applaudo%20Studios&origin=SWITCH_SEARCH_VERTICAL&page={j+1}')
        print(f'Page: {j+1}')
        time.sleep(2)

        # Get posts url
        for i in wd.find_elements_by_xpath(f'//a[contains(@href,"{href}")]'):
            complete_url = i.get_attribute('href')
            posts[complete_url.split('?')[0]] = 1

    return list(posts)


def get_post_reactions(wd):
    reactors_name = []
    reactors_href = []
    reactions_type = []

    reactions_window_btn = 'v-align-middle.social-details-social-counts__reactions-count'
    reactions_window_class_name = 'artdeco-modal__content.social-details-reactors-modal__content.ember-view'
    reactors_href_class_name = 'link-without-hover-state.ember-view'
    reactors_name_class_name = 'artdeco-entity-lockup__title.ember-view'
    reaction_class_name = 'reactions-icon.social-details-reactors-tab-body__icon.reactions-icon__consumption--small'
    modal_reactions_cn = 'social-details-reactors-tab-body'

    reactions_dataframe = pd.DataFrame(
        columns=['post_url', 'username', 'profile_url', 'reaction'])

    # opening reactions window

    try:
        reactions = wd.find_element_by_class_name(reactions_window_btn)
    except:
        reactions_dataframe = reactions_dataframe.append({'post_url': wd.current_url,
                                                          'username': '', 'profile_url': '', 'reaction': ''},
                                                         ignore_index=True)
        return reactions_dataframe

    n_reactions = int(reactions.text.replace(',', ''))
    reactions.click()

    time.sleep(2)

    reactions_modal = wd.find_element_by_xpath(
        "//div[@class='social-details-reactors-tab-body']")

    # scroll down in reactions window
    panel = wd.find_element_by_class_name(reactions_window_class_name)
    for i in range(int(n_reactions/10)+1):
        wd.execute_script(
            'arguments[0].scrollTop = arguments[0].scrollHeight', panel)
        time.sleep(2)
        try:
            wd.find_element_by_xpath("//*[text()='Show more results']").click()
        except:
            pass

    for reactor in reactions_modal.find_elements_by_class_name(reactors_href_class_name):
        reactors_href.append(reactor.get_attribute('href'))

    for reactor in reactions_modal.find_elements_by_class_name(reactors_name_class_name):
        reactors_name.append(reactor.text)

    for reaction in reactions_modal.find_elements_by_class_name(reaction_class_name):
        reactions_type.append(reaction.get_attribute('alt'))

    reactions_dataframe['post_url'] = [
        wd.current_url for i in range(len(reactors_name))]
    reactions_dataframe['username'] = reactors_name
    reactions_dataframe['profile_url'] = reactors_href
    reactions_dataframe['reaction'] = reactions_type

    return reactions_dataframe


def get_load_more_btn(wd):
    try:
        return wd.find_element_by_xpath("//*[text()='Load more comments']")
    except:
        return 'Element not found'


def get_load_previous_btn(wd):
    try:
        return wd.find_element_by_class_name("//*[text()='Load previous replies']")
    except:
        return 'Element not found'


def get_load_more_rpl_btn(wd):
    try:
        return wd.find_element_by_xpath("//*[text()='Load more replies']")
    except:
        return 'Element not found'


def get_post_comments(wd):
    # https://www.linkedin.com/feed/update/urn:li:activity:6701686325306912768/
    #  select most relevant
    # click load more replies
    commentors_name = []
    commentors_href = []
    comments = []
    replies = []
    number_of_replies = []

    commentors_name_class_name = 'comments-post-meta__name-text.hoverable-link-text.mr1'
    commentors_href_class_name = 'ember-view.comments-post-meta__profile-link.t-16.t-black.t-bold.tap-target'
    comments_class_name = 'comments-comment-item__main-content.feed-shared-main-content--comment.t-14.t-black.t-normal'
    close_modal_btn_cn = 'artdeco-modal__dismiss.artdeco-button.artdeco-button--circle.artdeco-button--muted.artdeco-button--2.artdeco-button--tertiary.ember-view'

    try:
        wd.find_element_by_class_name(close_modal_btn_cn).click()
        time.sleep(1)
    except:
        pass

    # loading all comments
    load_more_btn = get_load_more_btn(wd)
    load_previous_btn = get_load_previous_btn(wd)
    load_more_rpl_btn = get_load_more_rpl_btn(wd)

    comments_dataframe = pd.DataFrame(
        columns=['post_url', 'username', 'profile_url', 'comment', 'number_replies'])

    try:
        wd.find_element_by_class_name(
            'comments-sort-order-toggle__trigger.artdeco-dropdown__trigger.artdeco-dropdown__trigger--placement-bottom.ember-view').click()
        wd.find_element_by_xpath("//*[text()='Most recent']").click()
    except:
        pass

    if len(wd.find_elements_by_class_name('comments-comments-list')) == 0:
        comments_dataframe = comments_dataframe.append({'post_url': wd.current_url,
                                                        'username': '', 'profile_url': '', 'comment': '', 'number_replies': ''},
                                                       ignore_index=True)
        return comments_dataframe

    while(load_previous_btn != 'Element not found'):
        load_previous_btn.click()
        time.sleep(2)
        load_previous_btn = get_load_previous_btn(wd)

    while(load_more_rpl_btn != 'Element not found'):
        load_more_rpl_btn.click()
        time.sleep(2)
        load_more_rpl_btn = get_load_more_rpl_btn(wd)

    while(load_more_btn != 'Element not found'):
        load_more_btn.click()
        time.sleep(3)
        load_more_btn = get_load_more_btn(wd)

    time.sleep(1)

    amount_of_main_comments = wd.find_elements_by_class_name(
        "comments-comment-item.comments-comments-list__comment-item")

    for commentor in wd.find_elements_by_class_name(commentors_name_class_name):
        commentors_name.append(commentor.text)

    for commentor in wd.find_elements_by_class_name(commentors_href_class_name):
        commentors_href.append(commentor.get_attribute('href'))

    for comment in wd.find_elements_by_class_name(comments_class_name):
        comments.append(comment.text)

    for i in range(1, len(amount_of_main_comments)+1):
        try:
            replies_of_comment = wd.find_element_by_xpath(
                f"//article[{i}]/div[6]/div[3]/div/div[3]/span[2]")
            replies.append(int(replies_of_comment.text.split(' ')[0]))
        except:
            replies.append(0)

    for i in replies:
        word = 'Reply' if i == 1 else 'Replies'
        number_of_replies.append(f'{i} {word}')

        for k in range(i):
            number_of_replies.append('Is a Reply')

    comments_dataframe['post_url'] = [
        wd.current_url for i in range(len(commentors_name))]
    comments_dataframe['username'] = commentors_name
    comments_dataframe['profile_url'] = commentors_href
    comments_dataframe['comment'] = comments
    comments_dataframe['number_replies'] = number_of_replies

    return comments_dataframe


def get_media(wd, post_elmt):
    media_url = ''
    media_type = 'Other'  # unknown o no media?

    try:
        media_url = post_elmt.find_element_by_class_name(
            'vjs-tech').get_attribute('src')
        media_type = 'Video'
    except:
        try:
            media_url = post_elmt.find_element_by_class_name(
                'tap-target.feed-shared-mini-update-v2__link-to-details-page.text-body-medium.ember-view').get_attribute('href')
            media_type = 'Shared LinkedIn post'
        except:
            try:
                media_url = post_elmt.find_element_by_class_name(
                    'app-aware-link.feed-shared-article__image-link.tap-target').get_attribute('href')
                media_type = 'Shared link outside LinkedIn'  # job or article or whatever
            except:
                try:
                    media_url = post_elmt.find_element_by_class_name(
                        'app-aware-link.feed-shared-article__meta.flex-grow-1.full-width.tap-target').get_attribute('href')
                    media_type = 'Shared link outside LinkedIn without image'
                except:
                    try:
                        media_url = post_elmt.find_element_by_class_name(
                            'app-aware-link.feed-shared-entity__content.display-flex').get_attribute('href')
                        media_type = 'Job offer posted on LinkedIn'
                    except:
                        try:
                            media_url = post_elmt.find_element_by_class_name(
                                'app-aware-link.tap-target.video-s-loader__play-link.play-video').get_attribute('href')
                            media_type = 'External video'
                        except:
                            images = post_elmt.find_elements_by_class_name(
                                'ivm-view-attr__img--centered.feed-shared-image__image.lazy-image.ember-view')
                            if len(images) == 1:
                                media_url = images[0].get_attribute('src')
                                media_type = 'Single image'
                            elif len(images) > 1:
                                media_url = []
                                for img in images:
                                    media_url.append(
                                        img.get_attribute('src'))
                                media_type = 'Multiple images'
                            else:
                                wd.switch_to.frame(
                                    wd.find_element_by_tag_name("iframe"))
                                carousel = wd.find_elements_by_class_name(
                                    'carousel-lazy-element')
                                if len(carousel) > 0:
                                    media_url = []
                                    for slide in carousel:
                                        media_url.append(
                                            slide.get_attribute('src'))
                                    media_type = 'Carousel'
                                    wd.switch_to.default_content()
                                else:
                                    wd.switch_to.default_content()

    return media_url, media_type


def get_post(wd):
    post_df = pd.DataFrame(
        columns=['post_url', 'author', 'author_url', 'author_type', 'description', 'media_type', 'media_url'])

    author_element_cn = 'app-aware-link.feed-shared-actor__container-link.relative.display-flex.flex-grow-1'
    author_name_cn = 'feed-shared-actor__name.t-14.t-bold.hoverable-link-text.t-black'
    post_description_cn = 'feed-shared-inline-show-more-text.feed-shared-update-v2__description.feed-shared-inline-show-more-text--minimal-padding.feed-shared-inline-show-more-text--expanded'

    post_element = wd.find_element_by_class_name('core-rail.update-outlet')
    author_url = post_element.find_element_by_class_name(
        author_element_cn).get_attribute('href').split('?')[0]
    author_name = post_element.find_element_by_class_name(author_name_cn).text
    author_type = 'Company' if author_url.find('company') != -1 else 'User'

    try:
        description = post_element.find_element_by_class_name(
            post_description_cn).text
    except:
        description = 'No description'

    try:
        source = post_element.get_attribute('src')
    except:
        source = 'No source'

    media_url, media_type = get_media(wd, post_element)

    post_df = post_df.append({'post_url': wd.current_url, 'author': author_name, 'author_url': author_url,
                              'author_type': author_type, 'description': description, 'media_type': media_type,
                              'media_url': media_url},
                             ignore_index=True)
    print('media_url', media_url)
    print('media_type', media_type)

    return post_df
