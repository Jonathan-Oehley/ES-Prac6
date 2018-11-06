/* AssemblySort.s */

/* OHLJON001 */
/* ADYBEN001 */

/* Registers */
/*
r0 - string for print f
r1 - data for print f
r4 - minimum value found
r5 - current value to compare
r6 - base address of array to be sorted
r7 - inner loop offset
r8 - outer loop offset
r9 - temporary copy of r4
*/

.data
array: .word 15,6,3,9	@array to be sorted

format: .asciz "%d"	@printing string for data

.balign 4
comma: .asciz ", "	@comma

.balign 4
newline: .asciz "\n"	@newline

.text
.global main
.func main

main:
	PUSH {r4, r5, r6, r7, r8, LR}	@store registers in stack to restore later
	mov r7, #0 			@setup loop counters
	mov r8, #0

outer_loop:
	mov r7, r8 			@inner loop counter starts at outer loop counter
	ldr r6, =array			@get base address
	ldr r4, [r6, r8]		@get first value

inner_loop:
	ldr r6, =array 			@get base address
	ldr r5, [r6, r7]		@get next value in inner loop
	cmp r5, r4			@check r5<r4
	blt swap

inner_cont:
	add r7, r7, #4			@increment inner offset
	cmp r7, #16			@check if reached the end of the inner loop
	blt inner_loop			@loop again if not at end
	add r8, r8, #4			@increment outer offset
	cmp r8, #16			@check if reach the end of the outer loop
	blt outer_loop			@loop again if not at end
	mov r8, #0			@reset outer loop offset
	b print				@branch to print the sorted array	

swap:
	mov r9, r4			@save copy of r4
	mov r4, r5			@r6 is new minimum value
	str r4, [r6, r8]		@store r6 in the outer loop location
	str r9, [r6, r7]		@store r4 in the inner loop location
	b inner_cont			@return to inner loop

commas: 				@branch here after first print
	ldr r0, =comma			@load comma string to print
	bl printf			@print comma and space

print:
	ldr r6, =array			@load base address of array
	ldr r0, =format			@load the printing format
	ldr r1, [r6,r8]			@load the data to be printed
	bl printf			@print data value
	add r8, r8, #4			@increment offset
	cmp r8, #16			@check if end of the array has been reached
	blt commas

end:
	ldr r0, =newline		@load newline character
	bl printf			@print newline character
	POP {r4, r5, r6, r7, r8, LR}	@restore registers
	bx lr 				@leave main	














































