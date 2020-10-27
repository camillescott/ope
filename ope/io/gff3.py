#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Camille Scott, 2019
# File   : gff3.py
# License: MIT
# Author : Camille Scott <camille.scott.w@gmail.com>
# Date   : 11.12.2019

from abc import abstractmethod, ABC
import csv
from itertools import count
import hashlib
import pandas as pd
import sys
import warnings

from .base import convert_dtypes, ChunkParser, EmptyFile, warn_empty
from ..utils import touch

gff_version = '3.2.1'


class GFF3Parser(ChunkParser):

    columns = [('seqid', str),
                ('source', str),
                ('type', str),
                ('start', int),
                ('end', int),
                ('score', float),
                ('strand', str),
                ('phase', float),
                ('attributes', str)]
    
    def __init__(self, filename, **kwargs):
        super(GFF3Parser, self).__init__(filename, **kwargs)

    @staticmethod
    def decompose_attr_column(col):
        d = {}
        for item in col.strip(';').split(';'):
            key, _, val = item.strip().partition('=')
            d[key] = val.strip('')
        return d

    def empty(self):
        df = super(GFF3Parser, self).empty()
        df['ID'] = None
        df['Name'] = None
        df['Target'] = None
        return df

    def __iter__(self):
        '''Yields DataFrames of length chunksize from a given
        GTF/GFF file.

        GFF3 uses a 1-based, fully closed interval. Truly the devil's format.

        We convert to proper 0-based, half-open intervals.

        Yields:
            DataFrame: Pandas DataFrame with the results.
        '''
        # Read everything into a DataFrame
        n_chunks = 0
        for group in  pd.read_table(self.filename,
                                    delimiter='\t',
                                    comment='#',
                                    names=[k for k,_ in self.columns],
                                    na_values='.',
                                    converters={'attributes': self.decompose_attr_column},
                                    chunksize=self.chunksize,
                                    header=None):
            
            # Generate a new DataFrame from the attributes dicts, and merge it in
            group.reset_index(drop=True, inplace=True)
            df = pd.merge(group, pd.DataFrame(list(group.attributes)),
                          left_index=True, right_index=True)
            del df['attributes']

            # Repent, repent!
            df.start = df.start - 1

            n_chunks += 1
            yield df


class GFF3Converter(ABC):

    def __init__(self, from_df, tag='', database='', ftype='sequence_feature'):
        self.from_df = from_df
        self.tag = tag
        self.database = database
        self.ftype = ftype

    @abstractmethod
    def source(self):
        pass

    @abstractmethod
    def seqid(self):
        pass
    
    @abstractmethod
    def feature_type(self):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def end(self):
        pass

    @abstractmethod
    def score(self):
        pass

    @abstractmethod
    def strand(self):
        pass

    @abstractmethod
    def phase(self):
        pass

    @abstractmethod
    def ID_attr(self, IDs):
        pass
    
    @abstractmethod
    def attr_from_row(self, row):
        ''' Should return a dict of the attributes names and values,
        generated from the given row in the source DataFrame.
        '''
        pass

    @staticmethod
    def generate_ID(row):
        return hashlib.sha1(row.to_json().encode()).hexdigest()

    def __call__(self):
        gff3_df = pd.DataFrame()
        gff3_df['seqid'] = self.seqid()
        gff3_df['source'] = self.source()
        gff3_df['type'] = self.feature_type()
        gff3_df['start'] = self.start()
        gff3_df['end'] = self.end()
        gff3_df['score'] = self.score()
        gff3_df['strand'] = self.strand()
        gff3_df['phase'] = self.phase()

        gff3_df['attributes'] = self.from_df.apply(lambda row: \
                                                       ';'.join(( f'{key}={value}' \
                                                           for key, value in self.attr_from_row(row).items() )), 
                                                   axis=1)

        IDs = gff3_df.apply(self.generate_ID, axis=1)
        gff3_df['attributes'] = 'ID=' + self.ID_attr(IDs) + ';' + gff3_df['attributes']

        GFF3Writer.mangle_coordinates(gff3_df)

        return gff3_df


class GFF3Writer(object):

    version_line = '##gff-version 3.2.1'

    def __init__(self, filename=None, converter=None, **converter_kwds):
        self.filename = filename
        self.converter = converter
        self.converter_kwds = converter_kwds
        self.created = False

    def convert(self, data_df):
        converter_func = self.converter(data_df, **self.converter_kwds)
        return converter_func()

    def write(self, data_df, version_line=True):
        '''Write the given data to a GFF3 file, using the converter if given.

        Generates an empty file if given an empty DataFrame.

        Args:
            version_line (bool): If True, write the GFF3 version line at the.
            Note that this will cause an existing file to be overwritten, but
            will only be added in the first call to `write`.
        '''

        if self.filename is None:
            raise ValueError('Trying to write to filename None! Give GFF3Writer'
                             ' a filename.')

        if len(data_df) == 0:
            warn_empty('Writing out an empty GFF3 file to {0}'.format(self.filename))
            touch(self.filename)
            return
            
        if not self.created and version_line is True:
            with open(self.filename, 'w') as fp:
                fp.write(self.version_line + '\n')

        with open(self.filename, 'a') as fp:
            self.created = True

            if self.converter is not None:
                data_df = self.convert(data_df)
            else:
                self.mangle_coordinates(data_df)

            data_df.to_csv(fp, sep='\t', na_rep='.', columns=[k for k, v in GFF3Parser.columns],
                           index=False, header=False, quoting=csv.QUOTE_NONE,
                           float_format='%.6e')

    @staticmethod
    def mangle_coordinates(gff3_df):
        '''Although 1-based fully closed intervals are of the Beast,
        we will respect the convention in the interests of peace between
        worlds and compatibility.

        Args:
            gff3_df (DataFrame): The DataFrame to "fix".
        '''
        gff3_df.start += 1


