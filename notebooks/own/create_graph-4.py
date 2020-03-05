class create_source_to_graph(object):
    
    def get_indent(self, line, replace_line_indent='    '):
        return_indent_num = 0
        split_lines = line.split(replace_line_indent)
        for split_line in split_lines:
            if len(split_line) > 0:
                break
            return_indent_num += 1
        return return_indent_num

    def get_collon(self, line, colon=':'):
        return (1 if len(line) > 0 and line[-1] == colon else 0)

    def sequense_create_edges(self, target_indent_num, target_source_lines, create_edges=[]):
        before_node_name = None
        before_indent_num = None
        for idx in range(0, len(target_source_lines)):
            node_name = self.n_str + str(idx).zfill(self.zfill_str)
            [indent_num, colon_flg, indent_before_after_num, line] = target_source_lines[idx]
            # line = line.replace('    ', '').replace('"', '\'')
            if len(line) == 0 or \
                (target_indent_num == 0 and indent_num > 0):
                continue
            elif target_indent_num > indent_num:
                # reset node
                before_node_name = None


            if before_node_name is not None and (target_indent_num == indent_num):
                create_edges.append((before_node_name, node_name))
            if target_indent_num == indent_num:
                before_node_name = node_name
            before_indent_num = indent_num

    def change_create_edges(self, target_source_lines, create_edges=[]):
        before_node_name = None
        before_indent_num = None
        for idx in range(0, len(target_source_lines)):
            node_name = self.n_str + str(idx).zfill(self.zfill_str)
            [indent_num, colon_flg, indent_before_after_num, line] = target_source_lines[idx]
            if len(line) == 0:
                continue
            # print(indent_num, colon_flg, indent_before_after_num, line)
            # print(indent_num, colon_flg, indent_before_after_num, before_indent_num, indent_num)
            if before_indent_num is not None and before_indent_num != indent_num:
                create_edges.append((before_node_name, node_name))

            before_indent_num = indent_num
            before_node_name = node_name

    def print_subgraph(self, parent_graph, target_json, tab='\t', cnt=0, start_node=None):
        before_node = None
        return_key = None
        add_node_flg = 0
        for key in target_json:
            if start_node is not None and add_node_flg == 0:
                add_node_flg = 1
                parent_graph.edge(start_node, key)
            if key.find('subgraph') > -1 or cnt == 0:
                if cnt == 0:
                    # subgraph
                    return_key = self.print_subgraph(parent_graph, target_json[key], cnt=cnt+1, start_node=before_node)
                else:
                    with parent_graph.subgraph(name=key) as sub:
                        sub.attr(label=key)
                        # subgraph
                        self.print_subgraph(parent_graph, target_json[key], cnt=cnt+1, start_node=before_node)
            else:
                # node
                print(tab*cnt, key, '\t', target_json[key])
                parent_graph.node(key, target_json[key]['label'])
            return_key = None
        return before_node

    def main(self):
        import importlib, inspect, graphviz, json
        module = importlib.import_module(self.import_module_name)
        source_lines = None
        if self.module_function_name is None:
            source_lines = inspect.getsourcelines(module)
        else:
            source_lines = inspect.getsourcelines(getattr(module, self.module_function_name))

        sources = source_lines[0]
        commentout_flg = 0
        def_line = 0
        total_indent_num = None
        replace_line_indent = '    '
        colon = ':'
        before_indent_num = 0
        result_source_lines = []
        before_parentheses = '('
        after_parentheses = ')'

        for idx in range(0, len(sources)):
            line = sources[idx].replace('\n', '')
            # if line.find('@') > -1 or line.find('def') > -1:
            #     def_line = 1
            if line.find('"""') > -1:
                if commentout_flg == 0:
                    commentout_flg = 1
                elif commentout_flg == 1:
                    commentout_flg = -1

            if def_line == 0 and commentout_flg == 0:
                if total_indent_num is None:
                    total_indent_num = self.get_indent(line)

                indent_num = self.get_indent(line)
                output_line = line[len(replace_line_indent*total_indent_num):]
                colon_flg = self.get_collon(output_line)
                msg = ''
                indent_before_after_num = None
                if indent_num == before_indent_num:
                    indent_before_after_num = 0
                elif indent_num > before_indent_num:
                    indent_before_after_num = 1
                elif indent_num < before_indent_num:
                    indent_before_after_num = -1
                split_before_line = output_line.split(before_parentheses)
                len_split_before_line = len(split_before_line) - 1
                split_after_line = output_line.split(after_parentheses)
                len_split_after_line = len(split_after_line) - 1
                result_source_lines.append([indent_num, colon_flg, indent_before_after_num, len_split_before_line, len_split_after_line, output_line])
                before_indent_num = indent_num
                
                
            def_line = 0
            if commentout_flg == -1:
                commentout_flg = 0

        recreate_result_source_lines = []
        z_fill_num = 2
        start_num = None
        source_idx = 0
        pop_counter = 0
        len_result_source_lines = len(result_source_lines)
        try:
            for idx in range(0, len_result_source_lines):
                if idx + pop_counter + 1 >= len_result_source_lines:
                    break
                [indent_num, colon_flg, indent_before_after_num, len_split_before_line, len_split_after_line, output_line] = result_source_lines[idx + pop_counter]
                if start_num is None:
                    start_num = indent_num
                indent_num = indent_num - start_num
                if len_split_before_line == len_split_after_line:
                    recreate_result_source_lines.append([indent_num, colon_flg, indent_before_after_num, output_line])
                else:
                    recreate_result_source_lines.append([indent_num, colon_flg, indent_before_after_num, output_line])
                    before_after_parentheses_sum = len_split_before_line
                    for line_idx in range(idx + 1, len(result_source_lines)):
                        [t_indent_num, t_colon_flg, t_indent_before_after_num, t_len_split_before_line, t_len_split_after_line, t_output_line] = result_source_lines[line_idx]
                        recreate_result_source_lines[-1][-1] += t_output_line.replace(replace_line_indent, '')
                        result_source_lines.pop(line_idx)
                        pop_counter += 1
                        before_after_parentheses_sum += t_len_split_before_line
                        if before_after_parentheses_sum >= t_len_split_after_line:
                            pop_counter -= 1
                            break
        except:
            pass

        svg_extension='svg'
        dot='.'
        file_path='./'
        file_name='activate-20200305-1'
        graph_type_str='Digraph'
        graph_type='Digraph'
        engine='dot'
        file_extension='svg'
        
        graph_source_list = []

        space_str = ' '
        before_brackets = '{'
        after_brackets = '}'
        subgraph_counter = 0
        before_indent_num = None
        colon = ':'
        commna = ','
        double_quotation ='"'
        before_node_name = None

        graph_source_list.append(before_brackets + double_quotation + 'g' + double_quotation + colon + before_brackets)
        subgraph_counter += 1

        for idx in range(0, len(recreate_result_source_lines)):
            add_str = ''
            node_name = double_quotation + self.n_str + str(idx).zfill(self.zfill_str) + double_quotation + colon
            [indent_num, colon_flg, indent_before_after_num, line] = recreate_result_source_lines[idx]
            line = line.replace('    ', '').replace('"', '\'')
            if len(line) == 0:
                continue
            if before_indent_num is None or before_indent_num == indent_num:
                graph_source_list.append('\t'*subgraph_counter + node_name + space_str + before_brackets + double_quotation + 'label' + double_quotation + colon + double_quotation + line + double_quotation + after_brackets + commna)
                
            elif before_indent_num < indent_num:
                change_indent_num = indent_num - before_indent_num
                add_str = double_quotation + 'subgraph' + self.n_str + str(idx).zfill(self.zfill_str) + double_quotation + colon + space_str + before_brackets
                for change_indent_num_idx in range(0, change_indent_num):
                    graph_source_list.append('\t'*subgraph_counter + add_str)
                    subgraph_counter += 1
                graph_source_list.append('\t'*subgraph_counter + node_name + space_str + before_brackets + double_quotation + 'label' + double_quotation + colon + double_quotation + line + double_quotation + after_brackets + commna)
            elif before_indent_num > indent_num:
                change_indent_num = before_indent_num - indent_num
                add_str = after_brackets + commna
                for change_indent_num_idx in range(0, change_indent_num):
                    subgraph_counter -= 1
                    graph_source_list.append('\t'*subgraph_counter + add_str)
                graph_source_list.append('\t'*subgraph_counter + node_name + space_str + before_brackets + double_quotation + 'label' + double_quotation + colon + double_quotation + line + double_quotation + after_brackets + commna)
            
            if before_node_name is not None:
                pass
            before_indent_num = indent_num
            before_node_name = node_name

        if subgraph_counter > 0:
            add_str = after_brackets
            for subgraph_counter_idx in range(0, subgraph_counter):
                subgraph_counter -= 1
                graph_source_list.append('\t'*subgraph_counter + add_str + commna)

        before_indent_num = None
        for idx in range(0, len(graph_source_list)):
            line = graph_source_list[idx]
            indent_num = self.get_indent(line, replace_line_indent='\t')
            if before_indent_num is not None:
                if before_indent_num -1 == indent_num:
                    graph_source_list[idx -1] = graph_source_list[idx -1][:-1]
            before_indent_num = indent_num
        graph_source_list[-1] = graph_source_list[-1][:-1]
        graph_source_list.append(after_brackets)

        indent_max = max([x[0] for x in recreate_result_source_lines])
        
        edges = []
        for idx in range(0, indent_max):
            self.sequense_create_edges(idx, recreate_result_source_lines, create_edges=edges)

        self.change_create_edges(recreate_result_source_lines, create_edges=edges)

        json_data = json.loads(''.join(graph_source_list))

        self.graph = getattr(graphviz, graph_type_str)(
            name='root',
            format=file_extension,
            engine=engine
        )
        self.print_subgraph(self.graph, json_data)


        self.graph.edges(edges)

        # graph

    def __init__(
        self,
        import_module_name,
        module_function_name=None):
        self.import_module_name = import_module_name
        self.module_function_name = module_function_name
        self.graph = None
        self.zfill_str = 2
        self.n_str = 'n'
        self.main()
