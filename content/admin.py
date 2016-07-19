from django.contrib import admin

from content.models import MainPageCarousel, DeseaseInfo, Item, Test, Article, ArticleItem

admin.site.register(MainPageCarousel)
admin.site.register(DeseaseInfo)
admin.site.register(Item)
admin.site.register(Test)

class ArticleItemInline(admin.TabularInline):
    model = ArticleItem

class ArticleAdmin(admin.ModelAdmin):
    inlines = [
        ArticleItemInline,
    ]
    
admin.site.register(Article, ArticleAdmin) 
