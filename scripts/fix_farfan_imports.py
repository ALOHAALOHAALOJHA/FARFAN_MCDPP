import libcst as cst
import libcst.matchers as m

OLD = "farfan_core.farfan_core"
NEW = "farfan_core"

class FixFarfanImports(cst.CSTTransformer):
    def leave_Import(self, original_node: cst.Import, updated_node: cst.Import) -> cst.Import:
        new_names = []
        for alias in updated_node.names:
            name_node = alias.name
            # Handle direct imports like 'import farfan_core.farfan_core.x'
            if isinstance(name_node, cst.Attribute):
                # We need to flatten the attribute to check the full name
                full_name = self._get_full_name(name_node)
                if full_name and full_name.startswith(OLD):
                    # Replace the prefix
                    new_full_name = full_name.replace(OLD, NEW, 1)
                    # Reconstruct the Attribute node (simplified for this specific case)
                    new_node = cst.parse_expression(new_full_name)
                    alias = alias.with_changes(name=new_node)
            elif isinstance(name_node, cst.Name) and name_node.value == OLD:
                 name_node = cst.Name(NEW)
                 alias = alias.with_changes(name=name_node)
            
            new_names.append(alias)
        return updated_node.with_changes(names=new_names)

    def leave_ImportFrom(
        self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom
    ) -> cst.ImportFrom:
        module = updated_node.module
        if module:
            full_name = self._get_full_name(module)
            if full_name and full_name.startswith(OLD):
                 new_full_name = full_name.replace(OLD, NEW, 1)
                 new_module = cst.parse_expression(new_full_name)
                 return updated_node.with_changes(module=new_module)
        return updated_node

    def _get_full_name(self, node: cst.BaseExpression) -> str | None:
        if isinstance(node, cst.Name):
            return node.value
        elif isinstance(node, cst.Attribute):
            base = self._get_full_name(node.value)
            if base:
                return f"{base}.{node.attr.value}"
        return None
