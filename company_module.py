import pandas as pd
import dart_fss as dart

api_key='f60bb69488d19533e2bdb54a05343f20979e4307'
dart.set_api_key(api_key)
crp_list = dart.get_corp_list()

class search_company():

    def search_table(cmp_list):
        basic_info = crp_list.find_by_corp_name(cmp_list, exactly=True)[0]
        fs = basic_info.extract_fs(bgn_de='20190101')

        # 'bs' 재무상태표, 'is' 손익계산서, 'cis' 포괄손익계산서, 'cf' 현금흐름표
        df_cis = fs['cis']
        df_bs = fs['bs']
        df_cf = fs['cf']

        df_cis.to_csv('data/포괄손익계산서/' + cmp_list + ' 포괄손익계산서.csv', index=False)
        df_bs.to_csv('data/재무상태표/' + cmp_list + ' 재무상태표.csv', index=False)
        df_cf.to_csv('data/현금흐름도/' + cmp_list + ' 현금흐름표.csv', index=False)

        return df_cis, df_bs, df_cf

    def cis_preprocessing(df_cis):
        df_cis_1 = df_cis.iloc[:, [1, 7, 8, 9]]
        df_cis_1.columns = ['', df_cis_1.columns[1][0], df_cis_1.columns[2][0], df_cis_1.columns[3][0]]
        df_cis_1 = df_cis_1.T
        df_cis_1 = df_cis_1.rename(columns=df_cis_1.iloc[0])
        df_cis_1 = df_cis_1.drop(df_cis_1.index[0])
        df_cis_1 = df_cis_1.reset_index().rename(columns={'index': 'date'})
        df_cis_1['date'] = df_cis_1['date'].str[9:]
        print('cis_proprocessing complete')

        return df_cis_1

    def bs_preprocessing(df_bs):
        df_bs_1 = df_bs.iloc[:, [1, 7, 8, 9]]
        df_bs_1.columns = ['', df_bs_1.columns[1][0], df_bs_1.columns[2][0], df_bs_1.columns[3][0]]
        df_bs_1 = df_bs_1.T
        df_bs_1 = df_bs_1.rename(columns=df_bs_1.iloc[0])
        df_bs_1 = df_bs_1.drop(df_bs_1.index[0])
        df_bs_1 = df_bs_1.reset_index().rename(columns={'index': 'date'})
        print('bs_preprocessing complete')

        return df_bs_1

    def cf_preprocessing(df_cf):
        df_cf_1 = df_cf.iloc[:, [1, 6, 7, 8]]
        df_cf_1.columns = ['', df_cf_1.columns[1][0], df_cf_1.columns[2][0], df_cf_1.columns[3][0]]
        df_cf_1 = df_cf_1.T
        df_cf_1 = df_cf_1.rename(columns=df_cf_1.iloc[0])
        df_cf_1 = df_cf_1.drop(df_cf_1.index[0])
        df_cf_1 = df_cf_1.reset_index().rename(columns={'index': 'date'})
        df_cf_1['date'] = df_cf_1['date'].str[9:]
        print('cf_preprocessing complete')

        return df_cf_1

    def total_dataframe(self, df_cis_1, df_bs_1, df_cf_1, cmp_list):
        data_total = pd.merge(df_cis_1, df_bs_1, on='date')
        data_total = pd.merge(data_total, df_cf_1, on='date')
        data_total.to_csv('data/total/' + cmp_list + ' total.csv', index=False)

        return data_total


