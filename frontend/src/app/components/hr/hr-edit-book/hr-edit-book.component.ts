import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { BookService } from '../../../services/book.service';

@Component({
  selector: 'app-hr-edit-book',
  templateUrl: './hr-edit-book.component.html',
  styleUrl: './hr-edit-book.component.css'
})
export class HrEditBookComponent implements OnInit {

  bookId: string = '';
  borrowedCopies: number = 0;
  loading: boolean = false;
  loadError: string = '';
  message: string = '';
  messageType: 'success' | 'error' | '' = '';

  book = {
    title: '',
    bookNumber: '',
    author: '',
    isbn: '',
    category: '',
    total_copies: 1
  };

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private bookService: BookService
  ) {}

  ngOnInit(): void {
    this.bookId = this.route.snapshot.paramMap.get('id') || '';
    this.loading = true;
    this.bookService.getBook(this.bookId).subscribe({
      next: (data: any) => {
        this.book.title = data.title;
        this.book.bookNumber = data.bookNumber;
        this.book.author = data.author;
        this.book.isbn = data.isbn;
        this.book.category = data.category || '';
        this.book.total_copies = data.total_copies;
        this.borrowedCopies = data.total_copies - data.available_copies;
        this.loading = false;
      },
      error: (err) => {
        if (err.status === 404) {
          this.loadError = 'Book not found.';
        } else {
          this.loadError = err.error?.detail || 'Failed to load book.';
        }
        this.loading = false;
      }
    });
  }

  isFormValid(): boolean {
    return (
      this.book.title.trim() !== '' &&
      this.book.bookNumber.trim() !== '' &&
      this.book.author.trim() !== '' &&
      this.book.isbn.trim() !== '' &&
      this.book.total_copies >= 1 &&
      this.book.total_copies >= this.borrowedCopies
    );
  }

  onSubmit(): void {
    if (!this.isFormValid()) return;
    this.message = '';
    this.messageType = '';

    this.bookService.updateBook(this.bookId, this.book).subscribe({
      next: () => {
        this.message = 'Book updated successfully.';
        this.messageType = 'success';
        window.scrollTo({ top: 0, behavior: 'smooth' });
        this.router.navigate(["/hr-get-all-books"])
      },
      error: (err) => {
        this.message = err.error?.detail || 'Failed to update book';
        this.messageType = 'error';
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    });
  }

  cancel(): void {
    this.router.navigate(['/hr-get-all-books']);
  }
}
