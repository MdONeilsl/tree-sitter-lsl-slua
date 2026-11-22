import json
from pathlib import Path

TEST_DIR = Path("tests/grammar/slua")

TEST_DEFINITIONS = [
    # --- 1. Literals & Primitives ---
    ("lit_number_decimal", "42_195.5e+2", ["number"]),
    ("lit_number_hex", "0xDEAD_BEEF", ["number"]),
    ("lit_number_bin", "0b1010_0101", ["number"]),
    ("lit_string_single", "'hello slua'", ["string"]),
    ("lit_string_double", '"hello slua"', ["string"]),
    ("lit_string_long", "[[long string block]]", ["string"]),
    ("lit_interpolated", "`Value is {x + 1}`", ["stringinterp"]),
    ("lit_nil", "nil", ["nil"]),
    ("lit_true", "true", ["true"]),
    ("lit_false", "false", ["false"]),
    ("lit_vararg", "...", ["..."]),


    # --- 2. Binary Operators (Complete Isolation) ---
    ("binop_add", "a + b", ["binexp"]),
    ("binop_sub", "a - b", ["binexp"]),
    ("binop_mul", "a * b", ["binexp"]),
    ("binop_div", "a / b", ["binexp"]),
    ("binop_floordiv", "a // b", ["binexp"]),
    ("binop_mod", "a % b", ["binexp"]),
    ("binop_pow", "a ^ b", ["binexp"]),
    ("binop_concat", "a .. b", ["binexp"]),
    ("binop_lt", "a < b", ["binexp"]),
    ("binop_le", "a <= b", ["binexp"]),
    ("binop_gt", "a > b", ["binexp"]),
    ("binop_ge", "a >= b", ["binexp"]),
    ("binop_eq", "a == b", ["binexp"]),
    ("binop_ne", "a ~= b", ["binexp"]),
    ("binop_and", "a and b", ["binexp"]),
    ("binop_or", "a or b", ["binexp"]),


    # --- 3. Unary Operators (Complete Isolation) ---
    ("unop_neg", "-a", ["unexp"]),
    ("unop_not", "not a", ["unexp"]),
    ("unop_len", "#a", ["unexp"]),


    # --- 4. Compound Assignments ---
    ("compound_add", "a += 1", ["assign"]),
    ("compound_sub", "a -= 1", ["assign"]),
    ("compound_mul", "a *= 2", ["assign"]),
    ("compound_div", "a /= 2", ["assign"]),
    ("compound_floordiv", "a //= 2", ["assign"]),
    ("compound_mod", "a %= 2", ["assign"]),
    ("compound_pow", "a ^= 2", ["assign"]),
    ("compound_concat", 'a ..= "x"', ["assign"]),


    # --- 5. Suffixed Expressions & Calls ---
    ("expr_identifier", "myVariable", ["identifier"]),
    ("member_access", "obj.prop", ["member"]),
    ("expr_method_call", "obj:method()", ["functioncall"]),
    ("expr_call_plain", "func(1, 2)", ["functioncall"]),
    ("expr_call_string", "print 'hello'", ["functioncall"]),
    ("expr_call_table", "process { x = 1 }", ["functioncall"]),
    ("expr_index", "arr[1]", ["index"]),
    ("expr_parenthesized", "(a + b)", ["paren"]),


    # --- 6. Advanced Expressions ---
    ("expr_type_assertion", '"hello" :: string', ["tassert"]),
    ("expr_ifelse", "if x > 0 then 1 elseif x < 0 then -1 else 0", ["ifelseexp"]),
    ("table_constructor_empty", "{}", ["tableconstructor"]),
    ("table_constructor_fields", "{ [1] = 'a', b = 2, c }", ["tableconstructor"]),


    # --- 7. Control Flow Statements ---
    ("if_statement", "if condition then doSomething() elseif other then doElse() else doDefault() end", ["ifstmt"]),
    ("stmt_while", "while x > 0 do x -= 1 end", ["whilestmt"]),
    ("stmt_repeat", "repeat x += 1 until x == 10", ["repstmt"]),
    ("stmt_for_numeric", "for i = 1, 10, 2 do print(i) end", ["forstmt"]),
    ("stmt_for_generic", "for k, v in pairs(t) do print(k, v) end", ["forstmt"]),
    ("stmt_do", "do local x = 1 end", ["dostmt"]),
    ("stmt_return", "return x, y, z", ["laststat"]),
    ("stmt_break", "break", ["laststat"]),
    ("stmt_continue", "continue", ["laststat"]),
    ("stmt_empty", ";", []),


    # --- 8. Declarations & Functions ---
    ("decl_local", "local x: number = 42", ["localstmt"]),
    ("decl_const", "const PI: number = 3.14", ["conststmt"]),
    ("decl_function", "function foo(a: string, ...: any): number return 0 end", ["fundef"]),
    ("decl_local_function", "local function bar() return end", ["lfuncdef"]),


    # --- 9. Type System Declarations ---
    ("type_alias_simple", "type ID = string", ["typedef"]),
    ("type_alias_union", "type Status = active | inactive", ["typedef"]),
    ("type_alias_intersection", "type Combined = A & B", ["typedef"]),
    ("type_alias_optional", "type Opt = string?", ["typedef"]),
    ("type_alias_generic", "type Map<K, V> = { [K]: V }", ["typedef"]),
    ("type_alias_function", "type Callback = (number, string) -> boolean", ["typedef"]),
    ("type_table_struct", "type Point = { read x: number, write y: number }", ["typedef"]),
    ("export_type_decl", "export type PublicType = string", ["typedef"]),
    ("type_function_decl", "type function Compute<T>(x: T): T return x end", ["typefunc"]),


    # --- 10. Ambient Declarations ---
    ("declare_var", "declare globalVar: string", ["declare"]),
    ("declare_func", "declare function mathLog(x: number): number", ["declare"]),
    ("declare_class", "declare class BaseWidget extends Widget end", ["declare"]),


    # --- 11. Attributes ---
    ("attribute", "@native function f() end", ["attribute"]),
    ("attr_bracket", "@[hot, cache] function f() end", ["attribute"]),


    # --- New 100% Coverage Additions ---
    ("type_dotted_path", "type Ref = Net.Http.Response", ["typedef"]),
    ("type_pack_default", "type Fun<T... = (string, number)> = () -> T...", ["typedef"]),


    # New tests for advanced SLua features and ambient definitions
    ("declare_extern_type", "declare extern type quaternion with x: number end", ["exttype"]),
    ("attribute_checked", "@checked declare function foo(): number", ["declfunc"]),
    ("attribute_deprecated", "@[deprecated {reason='Use bar'}] declare function foo(): number", ["declfunc"]),
    ("type_intersection", "type T = A & B", ["typedef"]),
    ("type_typeof", "export type rotation = typeof(quaternion)", ["typedef"]),


    ("type_string_literal", 'type T = "collision"', ["typedef", "string"]),
    ("expr_non_null", "local y = x!", ["nonnull"]),
    ("type_dotted_generic", "type T = Net.Http.Response<string>", ["typedef", "typemember"]),
    ("declare_extern_field_read", "declare extern type Foo with read x: number end", ["exttype"]),
    ("declare_extern_method", "declare extern type Foo with function bar(self): number end", ["exttype", "extfunc"]),


    ("type_function_variadic_type", "type F = (...any) -> ()", ["typedef", "FunctionType", "builtin"]),
    ("type_function_variadic_named", "type F = (a: number, ...string) -> ()", ["typedef", "FunctionType"]),
    ("type_function_generic_prefix", "type F = <T>(T) -> T", ["typedef", "FunctionType"]),
    ("type_function_generic_prefix2", "type F = <K, V>(K, V) -> K", ["typedef", "FunctionType"]),


    ("type_function_generic_prefix_named", "type F = <T>(x: T) -> T", ["typedef", "FunctionType"]),
    ("type_function_generic_prefix_multi", "type F = <K, V>(K, V) -> K", ["typedef", "FunctionType"]),
    ("type_function_generic_prefix_noarg", "type F = <T>() -> T", ["typedef", "FunctionType"]),


    ("type_params_multi", "type T<A, B> = { a: A, b: B }", ["typedef"]),
    ("type_member_generic", "type T = Net.Http.Response<string>", ["typedef"]),
    ("type_params_pack_default", "type F<T... = (string, number)> = (T...) -> ()", ["typedef"]),
    ("type_function_generic_named", "type F = <T>(x: T) -> T", ["typedef"]),
    ("type_function_generic_multi", "type F = <K, V>(K, V) -> K", ["typedef"]),


    ("type_variadic_postfix", "type T = A...", ["typedef"]),
    ("type_variadic_postfix_dotted", "type T = Net.Http.Response...", ["typedef"]),
    ("type_variadic_optional", "type T = A...?", ["typedef"]),
    ("declare_return_variadic_prefix", "declare function f(): ...any", ["declare"]),
    ("type_function_param_variadic_type", "type F = (A...) -> ()", ["typedef"]),
    ("type_function_return_variadic_type", "type F = () -> R...", ["typedef"]),
    ("type_function_full_pack", "type F = <A..., R...>(A...) -> R...", ["typedef"]),
    ("declare_full_pcall", "declare function pcall<A..., R...>(f: (A...) -> R..., ...: A...): (boolean, R...)", ["declare"]),


    ("type_function_attr", "type F = @checked (number) -> number", ["typedef"]),
    ("type_function_attr_bracket", "type F = @[native, checked] (number) -> number", ["typedef"]),
    ("declare_table_with_attr_func", "declare bit32: { arshift: @checked (n: number, i: number) -> number }", ["declare"]),


    ("type_list_variadic_ret", "type T = (a: number) -> (boolean, ...any)", ["typedef"]),
    ("type_list_variadic_generic", "type T = Array<boolean, ...any>", ["typedef"]),
    ("declare_resume_pack", "declare coroutine: { resume: (co: thread, ...any) -> (boolean, ...any) }", ["declare"]),


    ("type_paren_function", "type F = ((a: number) -> string)", ["typedef"]),
    ("type_paren_function_intersect", "type F = ((a: number) -> string) & ((a: string) -> number)", ["typedef"]),
    ("declare_paren_function_intersect", "declare x: { f: ((data: string, asBuffer: false?) -> string) & ((data: string, asBuffer: true) -> buffer) }", ["declare"]),


    ("type_intersection_attr_first", "type F = @checked ((a: number) -> string) & ((a: string) -> number)", ["typedef"]),
    ("type_intersection_attr_alone", "type F = @checked ((a: number) -> string)", ["typedef"]),
    ("type_function_attr_simple", "type F = @checked (number) -> number", ["typedef"]),
    ("declare_fn_attr_intersection", "declare x: { f: @checked ((data: string, asBuffer: false?) -> string) & ((data: string, asBuffer: true) -> buffer) }", ["declare"]),


    ("type_function_param_keyword_name", "type F = (number: number) -> ()", ["typedef"]),
    ("type_function_param_keyword_name_multi", "type F = (number: number, new_damage: number) -> ()", ["typedef"]),
    ("type_function_param_keyword_string", "type F = (string: string, boolean: boolean) -> ()", ["typedef"]),
    ("declare_attr_param_keyword_name", "declare x: { AdjustDamage: @[deprecated {use='adjustDamage'}](number: number, new_damage: number) -> () }", ["declare"]),

    ("index_plain", "a[b]", ["index"]),
    ("index_member", "a.b[c]", ["index", "member"]),
    ("index_call", "f()[i]", ["index", "functioncall"]),
    ("index_paren", "(a)[i]", ["index", "paren"]),
    ("index_chain", "a[b][c]", ["index"]),
    ("index_nonnull", "a![b]", ["index", "nonnull"]),

    ("type_variadic_plain", "type T = A...", ["typedef"]),
]


def generate_all():
    if TEST_DIR.exists():
        for old_file in TEST_DIR.glob("*.*"):
            if old_file.name not in ("full.slua", "full.json"):
                old_file.unlink()
        print(f"Cleared generated files in {TEST_DIR} (preserving full.slua/json)")
    
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    
    for name, code, expected_nodes in TEST_DEFINITIONS:
        file_path = TEST_DIR / f"{name}.slua"
        json_path = TEST_DIR / f"{name}.json"

        file_path.write_text(code.strip() + "\n", encoding="utf-8")
        meta = {
            "must_contain": expected_nodes,
            "expect_error": False
        }
        json_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
        
        print(f"Generated: {file_path.name}")

if __name__ == "__main__":
    generate_all()