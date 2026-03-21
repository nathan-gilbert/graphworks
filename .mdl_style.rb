# Markdownlint style configuration
# frozen_string_literal: true

all
exclude_rule 'MD024'
rule 'MD013', line_length: 100, ignore_code_blocks: true, tables: false
rule 'MD029', style: 'ordered'
