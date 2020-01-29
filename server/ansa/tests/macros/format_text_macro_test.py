# flake8: noqa: E501

import inspect
import unittest

from ansa.macros.format_text_width import format_text_macro


class LowercaseMacro(unittest.TestCase):

    maxDiff = None

    def test_format_text_macro(self):
        html = (
            "<p>Beautiful Soup offers a lot of tree-searching methods (covered below), "
            "and they mostly take the same arguments as find_all(): name, attrs, string, limit, "
            "and the keyword arguments.</p>"
            "<p>But the recursive argument is different: find_all() and find() are the only methods "
            "that support it. Passing recursive=False into a method like find_parents() wouldn’t be "
            "very useful.</p>"
        )

        new_html = inspect.cleandoc(
            """<p>Beautiful Soup offers a lot of tree-searching methods (covered
            below), and they mostly take the same arguments as find_all():
            name, attrs, string, limit, and the keyword arguments.</p><p>But the recursive argument is different: find_all() and find()
            are the only methods that support it. Passing recursive=False
            into a method like find_parents() wouldn’t be very useful.</p>"""
        )

        item = {"body_html": html}
        format_text_macro(item)
        self.assertEqual(item.get("body_html"), new_html)

        format_text_macro(item)
        self.assertEqual(item["body_html"], new_html)

    def test_missing_content(self):
        html = """<p id="text-ds1hj"> (di Amalia Angotti)
(ANSA) - TORINO, 29 GEN - Helmut Newton fotografo di moda, ma anche artista. Donne e ritratti vip. Apre al pubblico domani la retrospettiva Helmut Newton. Works, che dà il via alla stagione espositiva 2020 della Gam - Galleria Civica d'Arte Moderna e Contemporanea di Torino. Promossa dalla Fondazione Torino Musei e prodotta da Civita Mostre e Musei, con la Helmut Newton Foundation di Berlino, è un primo appuntamento in attesa della grande mostra che Berlino dedicherà a Newton nel mese di ottobre per celebrare il centenario della nascita e che nel 2022 sbarcherà, prima tappa internazionale, a Milano a Palazzo Reale.  Il progetto espositivo è di Matthias Harder, direttore della fondazione tedesca, che ha selezionato 68 fotografie con lo scopo di presentare un'ampia panoramica della carriera del grande fotografo: ritratti a personaggi famosi del Novecento, come Andy Warhol, Gianni Agnelli, Paloma Picasso, Catherine Deneuve, Anita Ekberg, Claudia Schiffer e Gianfranco Ferrè, servizi per importanti campagne di moda. Un insieme di opere che hanno raggiunto milioni di persone grazie anche alle riviste e ai libri su cui sono apparse. Nel percorso della mostra, in quattro sezioni, si spazia dagli anni Settanta con le numerose copertine di Vogue sino all'opera più tarda con il bellissimo ritratto di Leni Richensthal del 2000. Al centro le donne, il loro corpo, i nudi, ma anche l'interazione tra uomini e donne. Alla Gam sono esposti alcuni servizi realizzati per Mario Valentino e per Thierry Mugler nel 1998, oltre a una serie di fotografie ormai iconiche per le più importanti riviste di monda internazionali.<br/>
"Sono foto che parlano da sole", afferma Maurizio Cibrario, presidente della Fondazione Torino Musei. "Ancora la fotografia protagonista a Torino", sottolinea l'assessore comunale alla Cultura Francesca Leon. "La fotografia di Helmut Newton, che abbraccia più di cinque decenni - spiega Matthias Harder - sfugge a qualsiasi classificazione e trascende i generi, apportando eleganza, stile e voyeurismo nella fotografia di moda, esprimendo bellezza e glamour e realizzando un corpus fotografico che continua a essere inimitabile".
Uno dei set fotografici preferiti era il garage del suo condominio a Monaco, con modelle e auto parcheggiate disposte a formare un dialogo visivo. Helmut Newton morì improvvisamente il 23 gennaio 2004 a Los Angeles, prima di poter assistere alla completa realizzazione della Fondazione a lui dedicata.
Helmut Newton Works è il titolo del grande volume edito da Taschen che comprende anche le foto esposte in mostra e ne rappresenta idealmente il catalogo. (ANSA).</p>
"""
        item = {"body_html": html}
        format_text_macro(item)
        self.assertGreater(10, abs(len(item["body_html"]) - len(html)))
