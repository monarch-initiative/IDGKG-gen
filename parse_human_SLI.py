import gzip
import os
import wget
from collections import defaultdict
from utils.lookup import Lookup
from utils.ensembl_lookup import EnsemblLookup
import idg2sl
from idg2sl import *


# from utils.ensembl_lookup import ncbi2ensembl


def get_entrez_gene_map():
    """
    Download the file  ftp://ftp.ncbi.nih.gov/gene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz
    """
    urldir = 'ftp://ftp.ncbi.nih.gov/gene/DATA/GENE_INFO/Mammalia/'
    local_filename = 'Homo_sapiens.gene_info.gz'
    symbol2entrezID = defaultdict(str)
    if not os.path.exists(local_filename):
        url = os.path.join(urldir, local_filename)
        local_filename = wget.download(url)
    with gzip.open(local_filename, 'rt') as f:
        for line in f:
            if not line.startswith("9606"):
                continue  # non human homo sapiens
            fields = line.split('\t')
            entrez = fields[1]
            symbol = fields[2]
            symbol2entrezID[symbol] = entrez
    return symbol2entrezID


symbol2ncbi = Lookup().symbol2ncbi
symbol2ensembl = Lookup().symbol2ensembl
ncbi2ensembl = Lookup().ncbi2ensembl


luo2008 = idg2sl.parse_luo2009_supplemental_file_S3('data/luo2009.tsv', symbol2ncbi)
bommi2008 = idg2sl.parse_bommi_reddi_2008('data/bommi-reddy-2008.tsv', symbol2ncbi)


# Turner 2008
turner2008 = Turner2008Parser(symbol2ncbi, 'data/turner-PARP1-2008.tsv')
turner_list = turner2008.parse()


steckel2012 = idg2sl.parse_steckel_2012('data/steckel-2012-KRAS.tsv', symbol2ncbi)
lord2008 = idg2sl.parse_lord_2008('data/lord-PARP1-2008.tsv', symbol2ncbi)
toyoshima2008 = idg2sl.parse_toyoshima_2008('data/toyoshima-MYC-2008.tsv', symbol2ncbi)

shen2015 = idg2sl.parse_Shen2015('data/Shen_2015.tsv', symbol2ncbi)
pathak2015 = idg2sl.parse_pathak_2015(symbol2ncbi)  # 2 SL Interactions, hardcoded
srivas2016 = idg2sl.parse_srivas_2016('data/Srivas_2016.tsv', symbol2ncbi)
han2017 = idg2sl.parse_han_2017('data/Han2017_supplemental_table_1.tsv', symbol2ncbi)
wang2017 = idg2sl.parse_wang_2017('data/Wang2017_table5.tsv', symbol2ncbi)
shen2017 = idg2sl.parse_shen_2017('data/shen2017.tsv', symbol2ncbi)

manual = ManualEntry()
manual_list = manual.get_entries()

sli_lists = [luo2008, bommi2008, turner_list, steckel2012, lord2008, toyoshima2008, shen2015, srivas2016, han2017,
             wang2017, shen2017, manual_list]
# sli_lists = [shen2015]


n = 0
n_SL = 0
for sli_list in sli_lists:
    for sli in sli_list:
        # if n < 10:
        # print(sli.get_tsv_line())
        n += 1
        if sli.get_SL():
            n_SL += 1

print("We got %d interactions including %d synthetic lethal interactions" % (n, n_SL))


def save_SL_data(path, sli_lists):
    with open(path, 'w') as out_f:
        # out_f.write("Gen1,Gen2,weight\n")
        for sli_list in sli_lists:
            for sli in sli_list:
                if sli.get_SL():
                    out_f.write(sli.get_gene_A_symbol() + "\t" + sli.get_gene_B_symbol() + "\t")
                    out_f.write(str(sli.get_effect_size()) + "\n")


def save_SL_data_ncbi(path, sli_lists):
    with open(path, 'w') as out_f:
        # out_f.write("Gen1,Gen2,weight\n")
        for sli_list in sli_lists:
            for sli in sli_list:
                if sli.get_SL():
                    out_f.write(sli.get_gene_A_id().split(":")[1] + "\t" + sli.get_gene_B_id().split(":")[1] + "\t")
                    out_f.write(str(sli.get_effect_size()) + "\n")


def save_SL_data_ensembl(path, sli_lists):
    found, nfound = 0, 0
    with open(path, 'w') as out_f:
        # out_f.write("Gen1,Gen2,weight\n")
        for sli_list in sli_lists:
            for sli in sli_list:
                # if sli.get_SL():

                if not sli.get_gene_A_id().startswith("NCBI"):
                    geneA_id = ncbi2ensembl.get(sli.get_gene_A_id().split(":")[1])
                elif sli.get_gene_A_symbol() in symbol2ensembl:
                    geneA_id = symbol2ensembl.get(sli.get_gene_A_symbol())
                else:
                    geneA_id = "n/a"

                if sli.get_gene_B_id().startswith("NCBI") and sli.get_gene_B_id().split(":")[1] in ncbi2ensembl:
                    geneB_id = ncbi2ensembl.get(sli.get_gene_B_id().split(":")[1])
                elif sli.get_gene_B_symbol() in symbol2ensembl:
                    geneB_id = symbol2ensembl.get(sli.get_gene_B_symbol())
                else:
                    geneB_id = "n/a"

                if geneA_id.startswith("ENS"):
                    found += 1
                else:
                    # if geneA_id is not "n/a":
                    # print(geneA_id)
                    nfound += 1
                if geneB_id.startswith("ENS"):
                    found += 1
                else:
                    # if geneB_id is not "n/a":
                    # print(geneB_id)
                    nfound += 1
                out_f.write("SL_data\t" + geneA_id + "\t" + geneB_id + "\t" + str(sli.get_effect_size()) + "\n")
    print("Found %d genes, didn't find %d genes" % (found, nfound))
    print(nfound / (found + nfound))


file = "SL_graph.tsv"
ncbi_file = "SL_graph_ncbi.tsv"
ensembl_file = "SL_graph_ensembl.tsv"

# save_SL_data(file, sli_lists)
# save_SL_data_ncbi(ncbi_file, sli_lists)
save_SL_data_ensembl(ensembl_file, sli_lists)

# df = pd.read_csv(filename)
# print(df.head())
# Graphtype = nx.Graph()
# G = nx.from_pandas_edgelist(df, "Gen1", "Gen2", "weight")
# labels=nx.draw_networkx_labels(G, pos=nx.spectral_layout(G))
# nx.draw(G, with_labels = True)
# plt.show()
