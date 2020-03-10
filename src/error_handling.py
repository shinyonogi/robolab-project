
def try_except_zerodivisionerror #loop that break down when, the right calc / except ZeroDivisionError happen
    while True:
        try:
            #calc_coord(self)       (only possibility where ZerDivisionError could be?)
            # if angle_alpha != 0   (obligation?)
            break
        except ZeroDivisionError:
            angle_alpha = 1


def try_except_keyerror  # loop that break down when, the right input / except KeyError happend
#in planet
        for d in Direction:  # Case: if the shortest path is only a way between two coordinates
            try:
                if self.path_dictionary[start][d][0] == target:
                    return [(start, d)]
            except KeyError as e:  # Also to prevent KeyError
                continue
# in planet
        for i in self.path_dictionary:  # First: goes through the dictionary/coordinates (First key)
            for s in Direction:  # Second: goes through the direction (Second key)
                for t in self.path_dictionary:  # Third: goes through the coordinates again
                    try:
                        if self.path_dictionary[i][s][0] == t and matrix_row != matrix_column:
                            matrix[matrix_row][matrix_column] = self.path_dictionary[i][s][2]  # Add the distance when there's a way
                        elif matrix_row == matrix_column:
                            matrix[matrix_row][matrix_column] = 0  # The way to coordinate itself
                        else:
                            if matrix[matrix_row][matrix_column] == 0:
                                matrix[matrix_row][
                                    matrix_column] = 9999  # 9999 stands for Infinity (unreachable coordinates)
                        matrix_column += 1
                    except KeyError as e:  # To avoid KeyError
                        continue
                matrix_column = 0
            matrix_row += 1



def try_except_indexerror #(Where could that happen?)
    while True:
        try:

            break
        except IndexError:

#in planet
for i in self.path_dictionary:  # adds the paths that are next to each other as shortest path
    for d in Direction:
        try:
            j = self.path_dictionary[i][d][0]
            if i != j:
                shortest_path_dictionary[(i, j)][0].append((i, d))
        except:
            continue



def try_finally: #no matter what happen in the try-block, finally-block will be started (other possibility?)
    try:
        ...
    finally:
        print("There may or may not have been an exception.")



def try_exept_finally:  #???
    try:
        ...
    except ValueError:
        print...
    except ZeroDivisionError:
        print...
    finally:
        print("There may or may not have been an exception.")
