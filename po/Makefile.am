LANGS = it de
LANGMO = $(LANGS:=.mo)
LANGPO = $(LANGS:=.po)

EXTRA_DIST = $(LANGPO)

if UPDATE_PO
# the TRANSLATORS: allows putting translation comments before the to-be-translated line.
gbipboxclient.pot: $(top_srcdir)/src/*.py
	$(XGETTEXT) --no-wrap -L Python --from-code=UTF-8 -kpgettext:1c,2 --add-comments="TRANSLATORS:" -d @PACKAGE_NAME@ -s -o $@ $^

gbipboxclient.pot: gbipboxclient-py.pot
	sed --in-place gbipboxclient-py.pot --expression=s/CHARSET/UTF-8/
	$(MSGUNIQ) --no-wrap --no-location $^ -o $@

%.po: gbipboxclient.pot
	if [ -f $@ ]; then \
		$(MSGMERGE) --backup=none --no-wrap --no-location -s -N -U $@ $< && touch $@; \
	else \
		$(MSGINIT) -l $@ -o $@ -i $< --no-translator; \
	fi
endif

.po.mo:
	$(MSGFMT) -o $@ $<

BUILT_SOURCES = $(LANGMO)
CLEANFILES = $(LANGMO) gbipboxclient-py.pot gbipboxclient.pot

dist-hook: $(LANGPO)

install-data-local: $(LANGMO)
	for lang in $(LANGS); do \
		$(mkinstalldirs) $(DESTDIR)/usr/lib/enigma2/python/Plugins/Extensions/GBIpboxClient/locale/$$lang/LC_MESSAGES; \
		$(INSTALL_DATA) $$lang.mo $(DESTDIR)/usr/lib/enigma2/python/Plugins/Extensions/GBIpboxClient/locale/$$lang/LC_MESSAGES/GBIpboxClient.mo; \
		$(INSTALL_DATA) $$lang.po $(DESTDIR)/usr/lib/enigma2/python/Plugins/Extensions/GBIpboxClient/locale/$$lang.po; \
	done

uninstall-local:
	for lang in $(LANGS); do \
		$(RM) $(DESTDIR)/usr/lib/enigma2/python/Plugins/Extensions/GBIpboxClient/locale/$$lang/LC_MESSAGES/GBIpboxClient.mo; \
		$(RM) $(DESTDIR)/usr/lib/enigma2/python/Plugins/Extensions/GBIpboxClient/locale/$$lang.po; \
	done
