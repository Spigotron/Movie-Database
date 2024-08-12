import graphene
from app.models import db, Genre as GenreModel, Movie as MovieModel
from graphene_sqlalchemy import SQLAlchemyObjectType
from sqlalchemy.orm import Session

class Genre(SQLAlchemyObjectType):
    class Meta:
        model = GenreModel

class Movie(SQLAlchemyObjectType):
    class Meta:
        model = MovieModel

class Query(graphene.ObjectType):
    movie = graphene.Field(Movie, movie_id=graphene.ID(required=True))
    movies = graphene.List(Movie)
    genre = graphene.Field(Genre, genre_id=graphene.ID(required=True))
    genres = graphene.List(Genre)
    search_movies = graphene.List(Movie, title=graphene.String(), director=graphene.String(), year=graphene.Int())

    def resolve_genre(root, info, genre_id):
        genre = db.session.get(GenreModel, genre_id)
        return genre
    
    def resolve_genres(root, info):
        return db.session.execute(db.select(GenreModel)).scalars()

    def resolve_movie(root, info, movie_id):
        movie = db.session.get(MovieModel, movie_id)
        return movie

    def resolve_movies(root, info):
        return db.session.execute(db.select(MovieModel)).scalars()

    def resolve_search_movies(root, info, genre_id):
        query = db.select(MovieModel)
        if not genre_id:
            return f"There are no movies in that genre."
        else:
            query = query.where(MovieModel.genres.ilike(f'%{genre_id}%'))
        results = db.session.execute(query).scalars().all()
        return results
    
    def resolve_search_genres(root, info, movie_id):
        query = db.select(GenreModel)
        if not movie_id:
            return f"That movie doesn't have a genre."
        else:
            query = query.where(GenreModel.movies.ilike(f'%{movie_id}%'))
        results = db.session.execute(query).scalars().all()
        return results
    
class AddMovie(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        director = graphene.String(required=True)
        year = graphene.Int(required=True)
        genres = graphene.String(required=True)

    movie = graphene.Field(Movie)

    def mutate(root, info, title, director, year, genres):
        with Session(db.engine) as session:
            with session.begin():
                movie = MovieModel(title=title, director=director, year=year, genres=genres)
                session.add(movie)

            session.refresh(movie)
            return AddMovie(movie=movie)
        
class CreateGenre(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        movies = graphene.String(required=True)

    genre = graphene.Field(Genre)

    def mutate(root, info, name, movies):
        with Session(db.engine) as session:
            with session.begin():
                genre = GenreModel(name=name, movies=movies)
                session.add(genre)

            session.refresh(genre)
            return CreateGenre(genre=genre)

class UpdateMovie(graphene.Mutation):
    class Arguments:
        movie_id = graphene.Int(required=True)
        title = graphene.String()
        director = graphene.String()
        year = graphene.Int()
        genres = graphene.String()

    movie = graphene.Field(Movie)

    def mutate(root, info, movie_id, title=None, director=None, year=None, genres=None):
        movie = db.session.get(MovieModel, id)
        if not movie:
            return None
        if title:
            movie.title = title
        if director:
            movie.director = director
        if year:
            movie.year = year
        if genres:
            movie.genres = genres
        db.session.commit()
        return UpdateMovie(movie=movie)
    
class UpdateGenre(graphene.Mutation):
    class Arguments:
        genre_id = graphene.Int(required=True)
        name = graphene.String()
        movies = graphene.String()

    genre = graphene.Field(Genre)

    def mutate(root, info, genre_id, name=None, movies=None):
        genre = db.session.get(GenreModel, id)
        if not genre:
            return None
        if name:
            genre.name = name
        if movies:
            genre.movies = movies
        db.session.commit()
        return UpdateGenre(genre=genre)

class DeleteMovie(graphene.Mutation):
    class Arguments:
        movie_id = graphene.Int(required=True)

    message = graphene.String()

    def mutate(root, info, movie_id):
        movie = db.session.get(MovieModel, movie_id)
        if not movie:
            return DeleteMovie(message="That movie does not exist.")
        else:
            db.session.delete(movie)
            db.session.commit()
            return DeleteMovie(message="Success: Movie Deleted.")
        
class DeleteGenre(graphene.Mutation):
    class Arguments:
        genre_id = graphene.Int(required=True)

    message = graphene.String()

    def mutate(root, info, genre_id):
        genre = db.session.get(GenreModel, genre_id)
        if not genre:
            return DeleteGenre(message="That genre does not exist.")
        else:
            db.session.delete(genre)
            db.session.commit()
            return DeleteGenre(message="Success: Genre Deleted.")

class Mutation(graphene.ObjectType):
    add_movie = AddMovie.Field()
    update_movie = UpdateMovie.Field()
    delete_movie = DeleteMovie.Field()
    add_genre = CreateGenre.Field()
    update_genre = UpdateGenre.Field()
    delete_genre = DeleteGenre.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)