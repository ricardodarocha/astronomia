import os

def carregar_nasa():
    """Estrelas hospedeiras do NASA Exoplanet Archive (com cache)."""
    arq = os.path.join(CACHE_DIR, "nasa_hosts.csv")
    try:
        if not os.path.exists(arq):
            print("Baixando NASA Exoplanet Archive ...")
            r = requests.get(NASA_TAP, timeout=120)
            r.raise_for_status()
            with open(arq, "wb") as f:
                f.write(r.content)
        df = pd.read_csv(arq)
        df["lum"] = 10 ** df["st_lum"]          # st_lum = log10(L/Lsol)
        df = df.rename(columns={"st_teff": "teff"})
        return df[["hostname", "teff", "lum"]].dropna()
    except Exception as e:
        print(f"[aviso] Não foi possível obter dados da NASA: {e}")
        return pd.DataFrame(columns=["hostname", "teff", "lum"])


def carregar_hipparcos():
    """Catálogo Hipparcos via VizieR (com cache)."""
    arq = os.path.join(CACHE_DIR, "hipparcos_hr.csv")
    try:
        if not os.path.exists(arq):
            print("Baixando catálogo Hipparcos (VizieR) - pode demorar ...")
            from astroquery.vizier import Vizier
            v = Vizier(columns=["HIP", "Vmag", "Plx", "e_Plx", "B-V"], row_limit=-1)
            tab = v.get_catalogs("I/239/hip_main")[0].to_pandas()
            tab.to_csv(arq, index=False)
        t = pd.read_csv(arq).dropna(subset=["Vmag", "Plx", "e_Plx", "B-V"])
        t = t[(t["Plx"] > 0) & (t["e_Plx"] / t["Plx"] < 0.10)]   # boa paralaxe
        # t = t[(t["B-V"] > -0.35) & (t["B-V"] < 2.0)]
        mv = t["Vmag"] + 5 * np.log10(t["Plx"]) - 10             # M_V = V + 5 log(plx_mas) - 10
        return pd.DataFrame({"teff": bv_para_teff(t["B-V"]), "lum": mv_para_lum(mv)})
    except Exception as e:
        print(f"[aviso] Não foi possível obter o Hipparcos: {e}")
        return pd.DataFrame(columns=["teff", "lum"])