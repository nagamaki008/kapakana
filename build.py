from fontTools.designspaceLib import DesignSpaceDocument
from glyphsLib.cli import main
from fontTools.ttLib import TTFont, newTable
from pathlib import Path
import shutil, os
import ufo2ft
import ufoLib2
import statmake.classes
import statmake.lib

path = Path("sources")

def DSIG_modification(font:TTFont):
    # font["DSIG"] = newTable("DSIG")     #Don't need anymore
    # font["DSIG"].ulVersion = 1
    # font["DSIG"].usFlag = 0
    # font["DSIG"].usNumSigs = 0
    # font["DSIG"].signatureRecords = []
    font["head"].flags |= 1 << 3        #sets flag to always round PPEM to integer
    font["gasp"] = newTable("gasp")
    font["gasp"].gaspRange = {65535: 0x000A} #Font is shipping UNHINTED :D

print ("[Kapakana] Converting to UFO")
main(("glyphs2ufo", "sources/kapakana.glyphs"))

for ufo in path.glob("*.ufo"):
    exportFont = ufoLib2.Font.open(ufo)
    static_ttf = ufo2ft.compileTTF(exportFont, removeOverlaps=True)
    DSIG_modification(static_ttf)
    if "light" in str(ufo).lower():
        static_ttf["OS/2"].usWeightClass = 300

    print ("["+str(ufo).split("/")[1][:-4]+"] Saving")
    static_ttf.save("fonts/ttf/"+str(ufo).split("/")[1][:-4]+".ttf")

print ("[Kapakana] Creating variable font")

designspace = DesignSpaceDocument.fromfile("sources/kapakana.designspace")
designspace.loadSourceFonts(ufoLib2.Font.open)

varFont = ufo2ft.compileVariableTTF(designspace, inplace=True)
styleSpace = statmake.classes.Stylespace.from_file("sources/STAT.plist")
statmake.lib.apply_stylespace_to_variable_font(styleSpace, varFont, {})
DSIG_modification(varFont)
varFont.save("fonts/variable/Kapakana[wght].ttf")

for ufo in path.glob("*.ufo"):
    shutil.rmtree(ufo)
os.remove("sources/kapakana.designspace")