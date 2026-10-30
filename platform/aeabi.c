#include <stddef.h>
void *memcpy(void *, const void *, size_t);
void *memmove(void *, const void *, size_t);
void *memset(void *, int, size_t);
void __aeabi_memcpy(void *d, const void *s, size_t n) { (void)memcpy(d, s, n); }
void __aeabi_memcpy4(void *d, const void *s, size_t n) { (void)memcpy(d, s, n); }
void __aeabi_memcpy8(void *d, const void *s, size_t n) { (void)memcpy(d, s, n); }
void __aeabi_memmove(void *d, const void *s, size_t n) { (void)memmove(d, s, n); }
void __aeabi_memset(void *d, size_t n, int c) { (void)memset(d, c, n); }
void __aeabi_memset4(void *d, size_t n, int c) { (void)memset(d, c, n); }
void __aeabi_memset8(void *d, size_t n, int c) { (void)memset(d, c, n); }
void __aeabi_memclr(void *d, size_t n) { (void)memset(d, 0, n); }
void __aeabi_memclr4(void *d, size_t n) { (void)memset(d, 0, n); }
void __aeabi_memclr8(void *d, size_t n) { (void)memset(d, 0, n); }
