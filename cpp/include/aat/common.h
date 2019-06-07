#pragma once

#define ENUM_TO_STRING(type) std::string type##_to_string(type typ) { return type##_names[static_cast<int>(typ)]; }
#define ENUM_FROM_STRING(type) type type##_from_string(char *s) { return _##type##_mapping[s]; }
