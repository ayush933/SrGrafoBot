import praw
import os
import time
from keep_alive import keep_alive

# TODO: Improve comment validation:
#      1. Implement subreddit blacklisting
#      2. Regex for imgur detection
#      3: Comment body length check

reddit = praw.Reddit(
    client_id=os.getenv("client_id"),
    client_secret=os.getenv("client_secret"),
    username=os.getenv("username"),
    password=os.getenv("password"),
    user_agent="edit bot (by u/Sr-grafo-edits)",
)
reddit.validate_on_submit = True
ini_reply = """
|Comment|Edit|Link|
|:-:|:-:|:-:|
"""
db = {}


def normalize(s):
    s = s.replace('\n', ' ')
    s = s.replace('>', "")
    s.replace('!', "")
    s.replace('`', "")
    s.replace("#", "")
    s.replace('_', "")
    return s


def valid(comment):
    if not comment.is_submitter or not comment.parent_id[1] == "1":
        return False
    if "edit" not in comment.body.lower():
        return False


def main():
    for comment in reddit.redditor("SrGrafo").stream.comments(skip_existing=True):
        if not valid(comment):
            continue
        par_submission = comment.submission
        par_comment_text = reddit.comment(id=comment.parent_id[3:]).body
        par_comment_text = normalize(par_comment_text)
        comment_text = normalize(comment.body)
        if max(len(par_comment_text), len(comment_text)) > 550:
            continue
        if par_submission.id not in db.keys():
            try:
                db[par_submission.id] = par_submission.reply(ini_reply + '\n').id
                print("New submission added to DB")
            except Exception as e:
                print("Failed to add submission to DB")
                print(f"Exception={e}")
                print(f"Submission ID={par_submission.id}")
                time.sleep(600)
                continue
        comment_to_edit = reddit.comment(id=db[par_submission.id])
        comment_link = """https://reddit.com""" + comment.permalink
        LINK = f"[Link]({comment_link})"
        s = f"{par_comment_text}|{comment_text}|{LINK}"
        reply = comment_to_edit.body + '\n' + s
        try:
            comment_to_edit.edit(reply)
            print("Edited Comment Succesfully")
            time.sleep(30)
        except Exception as e:
            print(f"Failed to edit comment.")
            print(f'Exception ={e}')
            print(f"Edit Comment = {comment_link}")


if __name__ == '__main__':
    # keep_alive()
    main()
