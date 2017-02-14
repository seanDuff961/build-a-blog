#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import re
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

#function def get_posts
#    post db query
def get_posts():
    posts = db.GqlQuery("select * from Post order by created desc limit 10")
    return posts
#Database post

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
        
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    
    def render (self, template, **kw):
        self.write(self.render_str(template, **kw))

class Posts(db.Model):
    #how you say something is a specific type
    #required = True sets constraint on the database - we need a title with the art
    subject = db.StringProperty(required=True)     
    content = db.TextProperty(required=True)  
    #automatically sets 'created' to be the current time
    created = db.DateTimeProperty(auto_now_add=True) 

#MainHandler
#blog
class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('<a href="/blog">blog</a>')
        
#BlogHandler / FrontPage Handler
#   mimic Asciichan

class BlogPageHandler(Handler):  
#   mimic Asciichan
    def render_front(self, subject="", content="", error=""):
        #taking variables and passing them into 
        #the template so we can use them in the form
        posts = db.GqlQuery("SELECT * FROM Posts ORDER BY created DESC")
        self.render("front.html", subject=subject, content=content, error=error, posts=posts)
    
    def get(self):
        self.render_front()
        
    def post(self):
        title = self.request.get("subject")
        content = self.request.get("content")
        
        #set page number and offset (all in the get, wherever you have get.self.main) 
        #fetch post for the user
        #deternmine next and previous page numberss
        #render the page
        #store page size and variable
        
          
#NewPosthandler
#class NewPostHandler(webapp2.RequestHandler):    
#    Render form
#    check title and body
#    if the title and body are both there, do something
#    do something if title and body are not there

class NewPost(Handler):
    #def get(self):
        #self.render("newpost.html")
        #blog_entry = Blog.get_by_id(int(id), parent=None)
        #error = ""
        #if not content
        #    error = "Incorrect Blog ID!"
        #return self.render("singlepost.html", blog_entry=blog_entry, error= error)
    def get(self):
        self.render("newpost.html")    

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Posts(subject = subject, content = content)
            p.put()
            self.redirect("/blog")
            #self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content, error=error)

    
#View Post Handler
#    (handles posts by ID - permalinks)
#    get posts by ID
#    check for 404 error
#    submissions.sort(key = lambda x: x.submitted_time)
  
#Do not add rot13 + others until you get these four working first

class ViewPostHandler(Handler):
    def get(self, id):
        error = ""
        post = Posts.get_by_id(int(id), parent=None)
        if not post:
            error = "Incorrect blog id!"
        
        return self.render("singlepost.html",post=post)
            
#pagination function
def get_posts(limit, offset):
    #query the database for posts, return them  
    posts = db.GqlQuery("select * from Post"
                        "order by created desc" 
                        "limit %s OFFSET %s" % (limit, offset))
    return posts
          


app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/blog', BlogPageHandler),
                               ('/blog/newpost', NewPost),
                               webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
                               ], debug=True)
