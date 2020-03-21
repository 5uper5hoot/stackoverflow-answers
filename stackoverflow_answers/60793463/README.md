Replacing Alembic base revision throws KeyError
===============================================
https://stackoverflow.com/questions/60793463/replace-alembic-base-revision-throws-keyerror#60793463

I am trying to replace Alembic base revision in a Flask application. The reason is that the Alembic revisions have not been created correctly for this project and I want to make them in correct order from initial database to the latest version. To do so, I had to create an initial revision and replaced it with the current base revision in the tree.
Here is what the tree looked like before any changes:
```
>> alembic history
20b081e106eb -> f6b6d50b4012 (head), revision 6
604059d119b3 -> 1f6f72cb12a9, revision 5
fa56f5d34a18 -> 604059d119b3, revision 4
4e8f28c411ea -> fa56f5d34a18, revision 3
8494e6010c15 -> 4e8f28c411ea, revision 2
37b8265891db -> 8494e6010c15, revision 1
<base> -> 37b8265891db, previous base
```
I changed the `down_revision` for the generated revision to `None` and set the `down_revision` for the previous base to the generated `revision_ID`. When I check the history, I see that everything is correctly in order and my new base revision is replaced with previous base and the previous base revises the generated base:
```
>> alembic history
20b081e106eb -> f6b6d50b4012 (head), revision 6
604059d119b3 -> 1f6f72cb12a9, revision 5
fa56f5d34a18 -> 604059d119b3, revision 4
4e8f28c411ea -> fa56f5d34a18, revision 3
8494e6010c15 -> 4e8f28c411ea, revision 2
37b8265891db -> 8494e6010c15, revision 1
47f0eb12e6b5 -> 37b8265891db, previous base
<base> -> 47f0eb12e6b5, initial database (new)
```
Now, when I run `alembic upgrade head`, I'm getting this error:
```
 File "/export/content/lid/apps/sec-assistant/dev-i001/libexec/sec-assistant_5a281323-d247-4339-afcf-79b88f9fab38/site-packages/alembic/script/base.py", line 329, in _upgrade_revs
        revs = list(revs)
      File "/export/content/lid/apps/sec-assistant/dev-i001/libexec/sec-assistant_5a281323-d247-4339-afcf-79b88f9fab38/site-packages/alembic/script/revision.py", line 652, in _iterate_revisions
        uppers = util.dedupe_tuple(self.get_revisions(upper))
      File "/export/content/lid/apps/sec-assistant/dev-i001/libexec/sec-assistant_5a281323-d247-4339-afcf-79b88f9fab38/site-packages/alembic/script/revision.py", line 300, in get_revisions
        resolved_id, branch_label = self._resolve_revision_number(id_)
      File "/export/content/lid/apps/sec-assistant/dev-i001/libexec/sec-assistant_5a281323-d247-4339-afcf-79b88f9fab38/site-packages/alembic/script/revision.py", line 433, in _resolve_revision_number
        self._revision_map
      File "/export/content/lid/apps/sec-assistant/dev-i001/libexec/sec-assistant_5a281323-d247-4339-afcf-79b88f9fab38/site-packages/alembic/util/langhelpers.py", line 240, in __get__
        obj.__dict__[self.__name__] = result = self.fget(obj)
      File "/export/content/lid/apps/sec-assistant/dev-i001/libexec/sec-assistant_5a281323-d247-4339-afcf-79b88f9fab38/site-packages/alembic/script/revision.py", line 151, in _revision_map
        down_revision = map_[downrev]
    KeyError: '47f0eb12e6b5'
```
Is there any way that I can fix this without deleting and regenerating all the revisions from base to head?

Cannot Reproduce with following steps:
======================================
`alembic.ini` configured to use a sqlite database `sqlalchemy.url = sqlite:///foo.db`.

1. Clone repo and `cd` into `60793463` directory.
2. Create (`python3.8 -m venv .venv --prompt venv`) and activate (`$ source .venv/bin/activate`) virtual env and `$ pip install -r requirements.txt`
3. Generate a first revision: `$ alembic revision -m 'first revision'`
4. Apply first revision: `$ alembic upgrade head`
5. Generate a second revision: `$ alembic revision -m 'second revision'`
6. Apply second revision: `$ alembic upgrade head`
7. Generate new first revision: `$ alembic revision -m 'new first revision'`
8. Modify new first revision module: `down_revision = None`
9. Copy revision identifier from new first revision module and paste to original first revision module `down_revision` attribute: `down_revision = "5b068c41f80f"`
10. Generate a "third" revision: `$ alembic revision -m 'third revision'`
11. Apply third revision: `$ alembic upgrade head` - all works.

To Reset
========
1. Run `alembic downgrade base`
2. Delete files in `versions` directory: `$ rm alembic/versions/*.py`
3. Start again at step 4