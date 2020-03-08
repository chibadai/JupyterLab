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

    def sequense_create_edges(self, target_indent_num, target_source_lines, sequense_edges=[]):
        before_node_name = None
        before_indent_num = None
        return_edges = []
        for idx in range(0, len(target_source_lines)):
            node_name = self.n_str + str(idx).zfill(self.zfill_str)
            [indent_num, colon_flg, indent_before_after_num, line] = target_source_lines[idx]
            if len(line) == 0 or \
                (target_indent_num == 0 and indent_num > 0):
                continue
            elif target_indent_num > indent_num:
                # reset node
                before_node_name = None


            if before_node_name is not None and (target_indent_num == indent_num):
                # sequense_edges.append((before_node_name, node_name))
                return_edges.append((before_node_name, node_name))
            if target_indent_num == indent_num:
                before_node_name = node_name
            before_indent_num = indent_num
        sequense_edges.append(return_edges)

    def change_create_edges(self, target_source_lines, change_edges=[]):
        before_node_name = None
        before_indent_num = None
        for idx in range(0, len(target_source_lines)):
            node_name = self.n_str + str(idx).zfill(self.zfill_str)
            [indent_num, colon_flg, indent_before_after_num, line] = target_source_lines[idx]
            if len(line) == 0:
                continue
            if before_indent_num is not None and before_indent_num != indent_num:
                change_edges.append((before_node_name, node_name))

            before_indent_num = indent_num
            before_node_name = node_name

    def print_subgraph(self, parent_graph, target_json, tab='\t', cnt=0, start_node=None):
        edges = []

        before_node = None
        add_node_flg = 0
        before_node_name = None
        for key in target_json:
            subgraph_label_name = None
            add_node_name = None
            if cnt == 0:
                # root json
                _ = self.print_subgraph(parent_graph, target_json[key], cnt=cnt+1, start_node=None)
                print(cnt, key)
            else:
                if key.find(self.subgraph_name) > -1:
                    subgraph_label_name = key + '_' + str(cnt)
                    # add_node_name = None
                    with parent_graph.subgraph(name=subgraph_label_name) as sub:
                        sub.attr(style='filled', color='blue')
                        sub.attr(label=subgraph_label_name)
                        # subgraph
                        add_node_name = self.print_subgraph(sub, target_json[key], cnt=cnt+1, start_node=before_node_name)
                else:
                    # node
                    add_node_name = key
                    parent_graph.node(add_node_name, target_json[key][self.label_name])
                
                if add_node_flg == 0 and start_node is not None and subgraph_label_name is None and add_node_name is not None:
                    add_node_flg = 1
                    # parent_graph.edge(start_node, add_node_name)
                    edges.append((start_node, add_node_name))

                if before_node_name is not None and add_node_name is not None:
                    edges.append((before_node_name, add_node_name))
                # print(start_node, before_node_name, add_node_name, subgraph_label_name)
                if add_node_name is not None:
                    before_node_name = add_node_name
        # self.sequense_edges.append(edges)
        if cnt != 0:
            parent_graph.edges(edges)

            return before_node_name
        else:
            return None

    def get_source_lines(self):
        commentout_flg = 0
        total_indent_num = None
        before_indent_num = 0

        for idx in range(0, len(self.sources)):
            line = self.sources[idx].replace('\n', self.blanck_str)
            if line.find('"""') > -1:
                if commentout_flg == 0:
                    commentout_flg = 1
                elif commentout_flg == 1:
                    commentout_flg = -1

            if commentout_flg == 0:
                if total_indent_num is None:
                    total_indent_num = self.get_indent(line)

                indent_num = self.get_indent(line)
                output_line = line[len(self.replace_line_indent*total_indent_num):]
                colon_flg = self.get_collon(output_line)
                msg = self.blanck_str
                indent_before_after_num = None
                if indent_num == before_indent_num:
                    indent_before_after_num = 0
                elif indent_num > before_indent_num:
                    indent_before_after_num = 1
                elif indent_num < before_indent_num:
                    indent_before_after_num = -1
                split_before_line = output_line.split(self.before_parentheses)
                len_split_before_line = len(split_before_line) - 1
                split_after_line = output_line.split(self.after_parentheses)
                len_split_after_line = len(split_after_line) - 1
                self.result_source_lines.append([indent_num, colon_flg, indent_before_after_num, len_split_before_line, len_split_after_line, output_line])
                before_indent_num = indent_num
                
                
            if commentout_flg == -1:
                commentout_flg = 0

    def edit_source_lines(self):
        start_num = None
        source_idx = 0
        pop_counter = 0
        len_result_source_lines = len(self.result_source_lines)
        try:
            for idx in range(0, len_result_source_lines):
                if idx + pop_counter + 1 >= len_result_source_lines:
                    break
                [indent_num, colon_flg, indent_before_after_num, len_split_before_line, len_split_after_line, output_line] = self.result_source_lines[idx + pop_counter]
                if start_num is None:
                    start_num = indent_num
                indent_num = indent_num - start_num
                if len_split_before_line == len_split_after_line:
                    self.recreate_result_source_lines.append([indent_num, colon_flg, indent_before_after_num, output_line])
                else:
                    self.recreate_result_source_lines.append([indent_num, colon_flg, indent_before_after_num, output_line])
                    before_after_parentheses_sum = len_split_before_line
                    for line_idx in range(idx + 1, len(self.result_source_lines)):
                        [t_indent_num, t_colon_flg, t_indent_before_after_num, t_len_split_before_line, t_len_split_after_line, t_output_line] = self.result_source_lines[line_idx]
                        self.recreate_result_source_lines[-1][-1] += t_output_line.replace(self.replace_line_indent, self.blanck_str)
                        self.result_source_lines.pop(line_idx)
                        pop_counter += 1
                        before_after_parentheses_sum += t_len_split_before_line
                        if before_after_parentheses_sum >= t_len_split_after_line:
                            pop_counter -= 1
                            break
        except:
            pass

    def make_source_lines_to_dot_language(self):
        subgraph_counter = 0
        before_indent_num = None
        before_node_name = None

        self.graph_source_list.append(self.before_brackets + self.double_quotation + 'g' + self.double_quotation + self.colon + self.before_brackets)
        subgraph_counter += 1

        for idx in range(0, len(self.recreate_result_source_lines)):
            add_str = self.blanck_str
            node_name = self.double_quotation + self.n_str + str(idx).zfill(self.zfill_str) + self.double_quotation + self.colon
            [indent_num, colon_flg, indent_before_after_num, line] = self.recreate_result_source_lines[idx]
            line = line.replace(self.replace_line_indent , self.blanck_str).replace(self.double_quotation, self.single_quotation)
            if len(line) == 0:
                continue
            if before_indent_num is None or before_indent_num == indent_num:
                self.graph_source_list.append(self.tab*subgraph_counter + node_name + self.space_str + self.before_brackets + self.double_quotation + self.label_name + self.double_quotation + self.colon + self.double_quotation + line + self.double_quotation + self.after_brackets + self.commna)
                
            elif before_indent_num < indent_num:
                change_indent_num = indent_num - before_indent_num
                add_str = self.double_quotation + self.subgraph_name + self.n_str + str(idx).zfill(self.zfill_str) + self.double_quotation + self.colon + self.space_str + self.before_brackets
                for change_indent_num_idx in range(0, change_indent_num):
                    self.graph_source_list.append(self.tab*subgraph_counter + add_str)
                    subgraph_counter += 1
                self.graph_source_list.append(self.tab*subgraph_counter + node_name + self.space_str + self.before_brackets + self.double_quotation + self.label_name + self.double_quotation + self.colon + self.double_quotation + line + self.double_quotation + self.after_brackets + self.commna)
            elif before_indent_num > indent_num:
                change_indent_num = before_indent_num - indent_num
                add_str = self.after_brackets + self.commna
                for change_indent_num_idx in range(0, change_indent_num):
                    subgraph_counter -= 1
                    self.graph_source_list.append(self.tab*subgraph_counter + add_str)
                self.graph_source_list.append(self.tab*subgraph_counter + node_name + self.space_str + self.before_brackets + self.double_quotation + self.label_name + self.double_quotation + self.colon + self.double_quotation + line + self.double_quotation + self.after_brackets + self.commna)
            
            if before_node_name is not None:
                pass
            before_indent_num = indent_num
            before_node_name = node_name

        if subgraph_counter > 0:
            add_str = self.after_brackets
            for subgraph_counter_idx in range(0, subgraph_counter):
                subgraph_counter -= 1
                self.graph_source_list.append(self.tab*subgraph_counter + add_str + self.commna)

        before_indent_num = None
        for idx in range(0, len(self.graph_source_list)):
            line = self.graph_source_list[idx]
            indent_num = self.get_indent(line, replace_line_indent=self.tab)
            if before_indent_num is not None:
                if before_indent_num -1 == indent_num:
                    self.graph_source_list[idx -1] = self.graph_source_list[idx -1][:-1]
            before_indent_num = indent_num
        self.graph_source_list[-1] = self.graph_source_list[-1][:-1]
        self.graph_source_list.append(self.after_brackets)

    def __init__(
        self,
        import_module_name,
        module_function_name=None,
        graph_type_str='Digraph',
        engine='dot',
        file_extension='svg',
        file_path='./',
        file_name='activate'):
        import importlib, inspect, graphviz, json
        
        self.graph_type_str = graph_type_str
        self.graph_type =self.graph_type_str
        self.engine = engine
        self.file_extension = file_extension
        self.svg_extension = self.file_extension
        self.file_path = file_path
        self.file_name = file_name
        self.import_module_name = import_module_name
        self.module_function_name = module_function_name

        self.dot = '.'
        self.graph = None
        self.zfill_str = 2
        self.n_str = 'n'
        self.replace_line_indent = '    '
        self.colon = ':'
        self.result_source_lines = []
        self.before_parentheses = '('
        self.after_parentheses = ')'
        self.space_str = ' '
        self.before_brackets = '{'
        self.after_brackets = '}'
        self.commna = ','
        self.double_quotation ='"'
        self.tab = '\t'
        self.subgraph_name = 'subgraph'
        self.label_name = 'label'
        self.blanck_str = ''
        self.single_quotation = '\''

        self.module = importlib.import_module(self.import_module_name)
        self.source_lines = None
        if self.module_function_name is None:
            self.source_lines = inspect.getsourcelines(module)
        else:
            self.source_lines = inspect.getsourcelines(getattr(self.module, self.module_function_name))
        self.sources = self.source_lines[0]
        self.get_source_lines()

        self.recreate_result_source_lines = []
        self.graph_source_list = []
        self.indent_max = None
        
        self.edit_source_lines()
        self.make_source_lines_to_dot_language()

        self.indent_max = max([x[0] for x in self.recreate_result_source_lines])
        
        # self.sequense_edges = []
        # self.change_edges = []
        # for idx in range(0, self.indent_max):
        #     self.sequense_create_edges(idx, self.recreate_result_source_lines, sequense_edges=self.sequense_edges)

        # self.change_create_edges(self.recreate_result_source_lines, change_edges=self.change_edges)
        # self.create_edges(self.recreate_result_source_lines, indent_max=self.indent_max, edges=self.edges)

        self.json_data = json.loads(self.blanck_str.join(self.graph_source_list))

        self.graph = getattr(graphviz, self.graph_type_str)(
            name='root',
            format=self.file_extension,
            engine=self.engine
        )
        self.print_subgraph(self.graph, self.json_data)


        # self.graph.edges(self.edges)
        # for edge_idx in range(0, len(self.sequense_edges)):
        #     self.graph.edges(self.sequense_edges[edge_idx])
        # self.graph.edges(self.change_edges)
        # print(self.sequense_edges)

    # def create_edges(self, source_lines, indent_max=0, edges=[]):
    #     for idx in range(0, indent_max):
    #         self.sequense_create_edges(idx, source_lines, create_edges=edges)

    #     self.change_create_edges(source_lines, create_edges=edges)

