from project import News_api as NA
import unittest
import pytest

class test_google_news_search (unittest.TestCase):
	def test_gn(self):
		#First check the GN search of this random long string yields no results.
		assert News_Search(News_Search_URL_Builder("hjhjdafdsfsdjfkjsndfnskvnskldfnmjksdnf;sdmfnsjfnkls5678d*nfjksnkvmlsmvksdkfl\\dkfjdskj=oq1", 1)) == []
		#Check the GN search for this very specific url that only has one old article and is probably not subject to change yields one search with publisher "El periódico de Aragón" (has been this way for 4yr now)
		assert News_Search('https://www.google.com/search?q=%22Ley+para+la+Reforma+Pol%C3%ADtica+de+Espa%C3%B1a%22&source=lnms&tbm=nws')[0][1] == "El Periódico de Aragón"
	#def test_bn(self):
