#!/usr/bin/python
# -*- coding: utf-8 -*-

import copy
from basecode import BaseCode, FieldType

class ext4_extent(BaseCode):
    _fields = [
        FieldType('uint32_t', 	'ee_block',       	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint16_t', 	'ee_len',         	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint16_t', 	'ee_start_hi',    	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint32_t', 	'ee_start_lo',    	**{"raw_field": "__le32", "reverse": True}      ),
    ]
    # [calculate_size]: class ext_extent, size=12

class ext4_extent_idx(BaseCode):
    _fields = [
        FieldType('uint32_t', 	'ei_block',       	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	'ei_leaf_lo',     	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint16_t', 	'ei_leaf_hi',     	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint16_t', 	'ei_unused',      	**{"raw_field": "__u16"}                        ),
    ]
    # [calculate_size]: class ext4_extent_idx, size=12

class ext4_extent_header(BaseCode):
    _fields = [
        FieldType('uint16_t', 	'eh_magic',       	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint16_t', 	'eh_entries',     	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint16_t', 	'eh_max',         	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint16_t', 	'eh_depth',       	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint32_t', 	'eh_generation',  	**{"raw_field": "__le32", "reverse": True}      ),
    ]
    # [calculate_size]: class ext4_extent_header, size=12


class ext4_inode(BaseCode):
    _type_map = copy.deepcopy(BaseCode._type_map)
    _type_map['ext4_extent'] = ('class', 'ext4_extent')
    _type_map['ext4_extent_header'] = ('class', 'ext4_extent_header')
    _type_map['ext4_extent_idx'] = ('class', 'ext4_extent_idx')
    _fields = [
        FieldType('uint16_t', 	'i_mode',         	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint16_t', 	'i_uid',          	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint32_t', 	'i_size_lo',      	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	'i_atime',        	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	'i_ctime',        	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	'i_mtime',        	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	'i_dtime',        	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint16_t', 	'i_gid',          	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint16_t', 	'i_links_count',  	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint32_t', 	'i_blocks_lo',    	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	'i_flags',        	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	'l_i_version',    	**{"raw_field": "__le32", "reverse": True}      ),  # 	union { struct {__le32  l_i_version;} linux1;} osd1;
        # FieldType('uint32_t', 	'h_i_translator', **{"raw_field": "__u32"}                        ),  # 	union { struct {__u32  h_i_translator;} hurd1;} osd1;
        # FieldType('uint32_t', 	'm_i_reserved1',  	**{"raw_field": "__u32"}                        ),  # 	union { struct {__u32  m_i_reserved1;} masix1;} osd1;

        # FieldType('uint32_t', 	'i_block[15]',    	**{"raw_field": "__le32", "reverse": True, "length": 15}),
        FieldType('ext4_extent_header', 	'i_block__ext4_extent_header',    	**{"raw_field": "struct ext4_extent_header"}),
        FieldType('ext4_extent_idx', 	'i_block__ext4_extent_idx',    	**{"raw_field": "struct ext4_extent_idx", "length": 4}),

        FieldType('uint32_t', 	'i_generation',   	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	'i_file_acl_lo',  	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	'i_size_high',    	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	'i_obso_faddr',   	**{"raw_field": "__le32", "reverse": True}      ),

        FieldType('uint16_t', 	'l_i_blocks_high',	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint16_t', 	'l_i_file_acl_high',	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint16_t', 	'l_i_uid_high',   	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint16_t', 	'l_i_gid_high',   	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint16_t', 	'l_i_checksum_lo',	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint16_t', 	'l_i_reserved',   	**{"raw_field": "__le16", "reverse": True}      ),

        # FieldType('uint16_t', 	'h_i_reserved1',  	**{"raw_field": "__le16", "reverse": True}      ),
        # FieldType('uint16_t', 	'h_i_mode_high',  	**{"raw_field": "__u16"}                        ),
        # FieldType('uint16_t', 	'h_i_uid_high',   	**{"raw_field": "__u16"}                        ),
        # FieldType('uint16_t', 	'h_i_gid_high',   	**{"raw_field": "__u16"}                        ),
        # FieldType('uint32_t', 	'h_i_author',     	**{"raw_field": "__u32"}                        ),

        # FieldType('uint16_t', 	'h_i_reserved1',  	**{"raw_field": "__le16", "reverse": True}      ),
        # FieldType('uint16_t', 	'm_i_file_acl_high',	**{"raw_field": "__le16", "reverse": True}      ),
        # FieldType('uint32_t', 	'm_i_reserved2[2]',	**{"raw_field": "__u32", "length": 2}                        ),

        FieldType('uint16_t', 	'i_extra_isize',  	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint16_t', 	'i_checksum_hi',  	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint32_t', 	'i_ctime_extra',  	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	'i_mtime_extra',  	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	'i_atime_extra',  	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	'i_crtime',       	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	'i_crtime_extra', 	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	'i_version_hi',   	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	'i_projid',       	**{"raw_field": "__le32", "reverse": True}      ),
    ]
    # [calculate_size]: class ext4_inode, size=160

class ext4_super_block(BaseCode):
    _fields = [
        FieldType('uint32_t', 	's_inodes_count',        	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_blocks_count_lo',     	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_r_blocks_count_lo',   	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_free_blocks_count_lo',	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_free_inodes_count',   	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_first_data_block',    	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_log_block_size',      	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_log_cluster_size',    	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_blocks_per_group',    	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_clusters_per_group',  	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_inodes_per_group',    	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_mtime',               	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_wtime',               	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint16_t', 	's_mnt_count',           	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint16_t', 	's_max_mnt_count',       	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint16_t', 	's_magic',               	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint16_t', 	's_state',               	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint16_t', 	's_errors',              	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint16_t', 	's_minor_rev_level',     	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint32_t', 	's_lastcheck',           	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_checkinterval',       	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_creator_os',          	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_rev_level',           	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint16_t', 	's_def_resuid',          	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint16_t', 	's_def_resgid',          	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint32_t', 	's_first_ino',           	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint16_t', 	's_inode_size',          	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint16_t', 	's_block_group_nr',      	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint32_t', 	's_feature_compat',      	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_feature_incompat',    	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_feature_ro_compat',   	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('char',     	's_uuid',                	**{"raw_field": "__u8", "length": 16}           ),
        FieldType('char',     	's_volume_name',         	**{"raw_field": "char", "length": 16}           ),
        FieldType('char',     	's_last_mounted',        	**{"raw_field": "char", "length": 64}           ),
        FieldType('uint32_t', 	's_algorithm_usage_bitmap',	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('char',     	's_prealloc_blocks',     	**{"raw_field": "__u8"}                         ),
        FieldType('char',     	's_prealloc_dir_blocks', 	**{"raw_field": "__u8"}                         ),
        FieldType('uint16_t', 	's_reserved_gdt_blocks', 	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('char',     	's_journal_uuid',        	**{"raw_field": "__u8", "length": 16}           ),
        FieldType('uint32_t', 	's_journal_inum',        	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_journal_dev',         	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_last_orphan',         	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_hash_seed',           	**{"raw_field": "__le32", "reverse": True, "length": 4}),
        FieldType('char',     	's_def_hash_version',    	**{"raw_field": "__u8"}                         ),
        FieldType('char',     	's_jnl_backup_type',     	**{"raw_field": "__u8"}                         ),
        FieldType('uint16_t', 	's_desc_size',           	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint32_t', 	's_default_mount_opts',  	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_first_meta_bg',       	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_mkfs_time',           	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_jnl_blocks',          	**{"raw_field": "__le32", "reverse": True, "length": 17}),
        FieldType('uint32_t', 	's_blocks_count_hi',     	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_r_blocks_count_hi',   	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_free_blocks_count_hi',	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint16_t', 	's_min_extra_isize',     	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint16_t', 	's_want_extra_isize',    	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint32_t', 	's_flags',               	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint16_t', 	's_raid_stride',         	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint16_t', 	's_mmp_update_interval', 	**{"raw_field": "__le16", "reverse": True}      ),
        FieldType('uint64_t', 	's_mmp_block',           	**{"raw_field": "__le64", "reverse": True}      ),
        FieldType('uint32_t', 	's_raid_stripe_width',   	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('char',     	's_log_groups_per_flex', 	**{"raw_field": "__u8"}                         ),
        FieldType('char',     	's_checksum_type',       	**{"raw_field": "__u8"}                         ),
        FieldType('char',     	's_encryption_level',    	**{"raw_field": "__u8"}                         ),
        FieldType('char',     	's_reserved_pad',        	**{"raw_field": "__u8"}                         ),
        FieldType('uint64_t', 	's_kbytes_written',      	**{"raw_field": "__le64", "reverse": True}      ),
        FieldType('uint32_t', 	's_snapshot_inum',       	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_snapshot_id',         	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint64_t', 	's_snapshot_r_blocks_count',	**{"raw_field": "__le64", "reverse": True}      ),
        FieldType('uint32_t', 	's_snapshot_list',       	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_error_count',         	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_first_error_time',    	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_first_error_ino',     	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint64_t', 	's_first_error_block',   	**{"raw_field": "__le64", "reverse": True}      ),
        FieldType('char',     	's_first_error_func',    	**{"raw_field": "__u8", "length": 32}           ),
        FieldType('uint32_t', 	's_first_error_line',    	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_last_error_time',     	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_last_error_ino',      	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_last_error_line',     	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint64_t', 	's_last_error_block',    	**{"raw_field": "__le64", "reverse": True}      ),
        FieldType('char',     	's_last_error_func',     	**{"raw_field": "__u8", "length": 32}           ),
        FieldType('char',     	's_mount_opts',          	**{"raw_field": "__u8", "length": 64}           ),
        FieldType('uint32_t', 	's_usr_quota_inum',      	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_grp_quota_inum',      	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_overhead_clusters',   	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_backup_bgs',          	**{"raw_field": "__le32", "reverse": True, "length": 2}),
        FieldType('char',     	's_encrypt_algos',       	**{"raw_field": "__u8", "length": 4}            ),
        FieldType('char',     	's_encrypt_pw_salt',     	**{"raw_field": "__u8", "length": 16}           ),
        FieldType('uint32_t', 	's_lpf_ino',             	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_prj_quota_inum',      	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_checksum_seed',       	**{"raw_field": "__le32", "reverse": True}      ),
        FieldType('uint32_t', 	's_reserved',            	**{"raw_field": "__le32", "reverse": True, "length": 98}),
        FieldType('uint32_t', 	's_checksum',            	**{"raw_field": "__le32", "reverse": True}      ),
    ]
    # [calculate_size]: class ext4_super_block, size=1024

def size_calc():
    ext4_super_block().calculate_size(True)

if __name__ == '__main__':
    size_calc()

__all__  =  (
             # 'ext4_extent',
             # 'ext4_extent_idx',
             # 'ext4_extent_header',
             'ext4_inode',
             'ext4_super_block',
             'size_calc',
             )