import { Component } from '@angular/core';
import { BookService } from '../../../services/book.service';
import { Router } from '@angular/router';
import { RequestService } from '../../../services/request.service';
import { AuthService } from '../../../services/auth.service';

@Component({
  selector: 'app-employee-get-all-books',
  templateUrl: './employee-get-all-books.component.html',
  styleUrl: './employee-get-all-books.component.css'
})
export class EmployeeGetAllBooksComponent {

  books: any[] = [];
  loading: boolean = false;
  errorMessage: string = '';

  successMessage: string = '';
  errorActionMessage: string = '';

  searchText: string = '';
  searchType: string = 'all';

  filteredBooks: any[] = [];

  constructor(
    private bookService: BookService,
    private router: Router,
    private requestService: RequestService,
    private authService: AuthService
  ) { }

  ngOnInit(): void {
    if (!this.authService.getToken()) {
      this.errorMessage = 'Please sign in to view available books.';
      return;
    }

    this.getAllBooks();
  }

  getAllBooks() {
    this.loading = true;
    this.errorMessage = '';

    this.bookService.getAllBooks().subscribe({
      next: (res: any) => {
        this.books = res;
        this.filteredBooks = res;
        this.loading = false;
      },
      error: (err) => {
        this.loading = false;
        this.errorMessage = this.getLoadErrorMessage(err);
        console.error(err);
      }
    });
  }

  private getLoadErrorMessage(err: any): string {
    if (err.status === 0) {
      return 'Unable to connect to the server. Please try again.';
    }

    if (err.status === 401) {
      return 'Your session expired. Please sign in again.';
    }

    if (err.status === 403) {
      return err.error?.detail || 'You do not have access to view available books.';
    }

    return err.error?.detail || 'Failed to load books.';
  }

  getDisplayIsbn(isbn: string | null | undefined): string {
    const value = isbn?.trim();

    if (!value || value.toLowerCase() === 'testing edit again') {
      return 'Unknown';
    }

    return value;
  }


  // Pagination Version
  // lastKey: any = null;

  // getAllBooks(loadMore: boolean = false) {
  //   this.loading = true;

  //   this.bookService.getAllBooks(9, this.lastKey).subscribe({
  //     next: (res: any) => {
  //       if (loadMore) {
  //         this.books = [...this.books, ...res.items];
  //       } else {
  //         this.books = res.items;
  //       }

  //       this.lastKey = res.last_key;
  //       this.loading = false;
  //     },
  //     error: () => {
  //       this.loading = false;
  //       this.errorMessage = 'Failed to load books';
  //     }
  //   });
  // }


  borrowBook(bookId: number) {
    this.clearMessages();

    this.requestService.borrow(bookId)
      .subscribe({
        next: (res) => {
          this.successMessage = 'Borrow request sent successfully.';
          setTimeout(() => this.clearMessages(), 3000);
          // alert('Borrow request sent');
        },
        error: (err) => {
          this.errorActionMessage = err.error?.detail || 'Borrow failed';
          setTimeout(() => this.clearMessages(), 3000);
          // alert(err.error.detail);
        }
      });
  }

  // renewBook(borrowId: number) {
  //   this.requestService.renew(borrowId)
  //     .subscribe({
  //       next: () => {
  //         this.successMessage = 'Renew Request Sent Successfully';
  //         // alert('Renew request sent');
  //       },
  //       error: (err) => {
  //         this.errorActionMessage = err.error?.detail || 'Renew Failed';
  //         // alert(err.error.detail);
  //       }
  //     });
  // }

  // returnBook(borrowId: number) {
  //   this.requestService.returnBook(borrowId)
  //     .subscribe({
  //       next: () => {
  //         this.successMessage = 'Return Request Sent Successfully';
  //         // alert('Return request sent');
  //       },
  //       error: (err) => {
  //         this.errorActionMessage = err.error?.detail || 'Return Failed';
  //         // alert(err.error.detail);
  //       }
  //     });
  // }

  applyFilter() {
    const text = this.searchText.toLowerCase();

    this.filteredBooks = this.books.filter(book => {
      if (this.searchType === 'title') {
        return book.title?.toLowerCase().includes(text);
      }

      if (this.searchType === 'author') {
        return book.author?.toLowerCase().includes(text);
      }

      if (this.searchType === 'category') {
        return book.category?.toLowerCase().includes(text);
      }

      // ALL
      return (
        book.title?.toLowerCase().includes(text) ||
        book.author?.toLowerCase().includes(text) ||
        book.category?.toLowerCase().includes(text)
      );
    });
  }





  clearMessages() {
    this.successMessage = '';
    this.errorActionMessage = '';
  }
}
